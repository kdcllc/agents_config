"""
Base mixin for environment variable substitution.
"""

import os
import re
from typing import Any


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

            def replace_env_var(match: re.Match) -> str:
                env_var = match.group(1)
                env_value = os.getenv(env_var)
                if env_value is None:
                    raise ValueError(
                        f"Environment variable '{env_var}' not found"
                    )
                return env_value

            return re.sub(pattern, replace_env_var, value)
        elif isinstance(value, dict):
            return {
                k: EnvSubstitutionMixin.substitute_env_vars(v) for k, v in value.items()
            }
        elif isinstance(value, list):
            return [EnvSubstitutionMixin.substitute_env_vars(item) for item in value]
        else:
            return value
