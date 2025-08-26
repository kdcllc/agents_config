"""
Base mixin for environment variable substitution and reference resolution.
"""

import os
import re
from typing import Any, Dict


class EnvSubstitutionMixin:
    """Mixin for environment variable substitution in string fields."""

    @staticmethod
    def substitute_env_vars(value: Any) -> Any:
        """
        Recursively substitute environment variables in format ${env:VAR_NAME}.

        Args:
            value: The value to process (can be str, dict, list, etc.)

        Returns:
            The value with environment variables substituted

        Raises:
            ValueError: If an environment variable is not found
        """
        if isinstance(value, str):
            # Pattern to match ${env:VAR_NAME}
            pattern = r"\$\{env:([^}]+)\}"

            def replace_env_var(match: re.Match[str]) -> str:
                env_var = match.group(1)
                env_value = os.getenv(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable '{env_var}' not found")
                return env_value

            return re.sub(pattern, replace_env_var, value)
        elif isinstance(value, dict):
            return {k: EnvSubstitutionMixin.substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [EnvSubstitutionMixin.substitute_env_vars(item) for item in value]
        else:
            return value


class ReferenceResolutionMixin:
    """Mixin for resolving internal configuration references."""

    @staticmethod
    def resolve_references(value: Any, config_dict: Dict[str, Any]) -> Any:
        """
        Recursively resolve internal references in format ${ref:path.to.value}.

        Args:
            value: The value to process (can be str, dict, list, etc.)
            config_dict: The full configuration dictionary for reference
                resolution

        Returns:
            The value with internal references resolved

        Raises:
            ValueError: If a reference path is not found
        """
        if isinstance(value, str):
            # Pattern to match ${ref:path.to.value}
            pattern = r"\$\{ref:([^}]+)\}"

            def replace_reference(match: re.Match[str]) -> str:
                ref_path = match.group(1)
                resolved_value = ReferenceResolutionMixin._resolve_path(ref_path, config_dict)
                if resolved_value is None:
                    raise ValueError(f"Reference path '{ref_path}' not found in configuration")
                return str(resolved_value)

            # Also handle simple references without ${ref:} wrapper
            # for backward compatibility with existing patterns
            if value in config_dict:
                return config_dict[value]

            # Handle dot notation references like "ai_foundry.tools.opoint_api"
            if "." in value and not value.startswith("${"):
                try:
                    resolved = ReferenceResolutionMixin._resolve_path(value, config_dict)
                    if resolved is not None:
                        return resolved
                except (KeyError, TypeError):
                    pass  # Not a reference, return as-is

            return re.sub(pattern, replace_reference, value)
        elif isinstance(value, dict):
            return {k: ReferenceResolutionMixin.resolve_references(v, config_dict) for k, v in value.items()}
        elif isinstance(value, list):
            return [ReferenceResolutionMixin.resolve_references(item, config_dict) for item in value]
        else:
            return value

    @staticmethod
    def _resolve_path(path: str, config_dict: Dict[str, Any]) -> Any:
        """
        Resolve a dot-notation path in the configuration dictionary.

        Args:
            path: Dot-notation path like "ai_foundry.default_project_endpoint"
            config_dict: The configuration dictionary

        Returns:
            The resolved value or None if not found
        """
        parts = path.split(".")
        current = config_dict

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current
