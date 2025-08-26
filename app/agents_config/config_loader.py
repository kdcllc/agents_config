"""
Configuration loader utilities.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import ValidationError

from .ai_config import AIConfig
from .base import EnvSubstitutionMixin, ReferenceResolutionMixin


class ConfigLoader:
    """Utility class for loading and validating AI configurations."""

    @staticmethod
    def load_from_file(config_path: str) -> AIConfig:
        """
        Load configuration from YAML file with reference resolution.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Validated AIConfig instance with resolved references

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValidationError: If configuration validation fails
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML file {config_path}: {e}")

        if raw_config is None:
            raise ValueError(f"Configuration file {config_path} is empty")

        # First pass: resolve environment variables
        config_with_env = EnvSubstitutionMixin.substitute_env_vars(raw_config)

        # Second pass: resolve internal references
        config_with_refs = ReferenceResolutionMixin.resolve_references(config_with_env, config_with_env)

        try:
            return AIConfig(**config_with_refs)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed for {config_path}: {e}")

    @staticmethod
    def load_from_dict(config_dict: Dict[str, Any]) -> AIConfig:
        """
        Load configuration from dictionary with reference resolution.

        Args:
            config_dict: Configuration as dictionary

        Returns:
            Validated AIConfig instance with resolved references

        Raises:
            ValidationError: If configuration validation fails
        """
        # First pass: resolve environment variables
        config_with_env = EnvSubstitutionMixin.substitute_env_vars(config_dict)

        # Second pass: resolve internal references
        config_with_refs = ReferenceResolutionMixin.resolve_references(config_with_env, config_with_env)

        try:
            return AIConfig(**config_with_refs)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    @staticmethod
    def validate_environment_variables(config: AIConfig) -> List[str]:
        """
        Validate that all required environment variables are set.

        Args:
            config: The configuration to validate

        Returns:
            List of missing environment variable names
        """
        import re

        missing_vars = []

        def extract_env_vars(value: Any) -> List[str]:
            """Extract environment variable names from a value."""
            env_vars = []
            if isinstance(value, str):
                pattern = r"\$\{env:([^}]+)\}"
                matches = re.findall(pattern, value)
                env_vars.extend(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    env_vars.extend(extract_env_vars(v))
            elif isinstance(value, list):
                for item in value:
                    env_vars.extend(extract_env_vars(item))
            return env_vars

        # Extract all environment variables from config
        config_dict = config.model_dump()
        required_vars = extract_env_vars(config_dict)

        # Check if each variable is set
        for var in set(required_vars):
            if os.getenv(var) is None:
                missing_vars.append(var)

        return missing_vars

    @staticmethod
    def create_example_config() -> Dict[str, Any]:
        """
        Create an example configuration dictionary.

        Returns:
            Example configuration as dictionary
        """
        return {
            "version": "1.0",
            "models": {
                "gpt-4": {
                    "provider": "azure_openai",
                    "id": "gpt-4",
                    "version": "2024-02-15-preview",
                    "config": {
                        "api_key": "${env:AZURE_OPENAI_API_KEY}",
                        "endpoint": "${env:AZURE_OPENAI_ENDPOINT}",
                        "api_version": "2024-02-15-preview",
                    },
                    "params": {
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "top_p": 0.9,
                    },
                },
                "gpt-3.5-turbo": {
                    "provider": "azure_openai",
                    "id": "gpt-3.5-turbo",
                    "version": "2024-02-15-preview",
                    "config": {
                        "api_key": "${env:AZURE_OPENAI_API_KEY}",
                        "endpoint": "${env:AZURE_OPENAI_ENDPOINT}",
                        "api_version": "2024-02-15-preview",
                    },
                    "params": {
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "top_p": 0.9,
                    },
                },
            },
            "tools": {
                "openapi": {
                    "weather": {
                        "name": "weather",
                        "description": "Get weather information",
                        "schema_path": "tools/openapi/weather.json",
                        "base_url": "https://api.weather.com",
                    }
                },
                "ai_foundry": {
                    "tools": {
                        "bing": {
                            "name": "bing",
                            "description": "Bing search tool",
                            "connection_id": "${env:BING_CONNECTION_ID}",
                            "container_name": "bing-search",
                        }
                    }
                },
            },
            "agents": {
                "assistant": {
                    "version": "1.0",
                    "name": "Assistant",
                    "description": "General purpose AI assistant",
                    "model": {"name": "gpt-4", "temperature": 0.7},
                    "tools": ["openapi.weather", "ai_foundry.tools.bing"],
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "prompts/assistant.md"},
                },
                "search_agent": {
                    "version": "1.0",
                    "name": "Search Agent",
                    "description": "Specialized search agent",
                    "model": {"name": "gpt-3.5-turbo", "temperature": 0.3},
                    "tools": ["ai_foundry.tools.bing"],
                    "platform": "azure_openai",
                    "system_prompt": {
                        "version": "1.0",
                        "path": "prompts/search-agent.md",
                    },
                },
            },
        }

    @staticmethod
    def save_example_config(output_path: str) -> None:
        """
        Save an example configuration to a YAML file.

        Args:
            output_path: Path where to save the example configuration
        """
        example_config = ConfigLoader.create_example_config()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False, indent=2)
