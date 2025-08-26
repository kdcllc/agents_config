"""
Pydantic models for AI configuration with environment variable substitution.

This module provides robust validation and type safety for the AI configuration
YAML files, with automatic environment variable resolution.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.types import PositiveFloat, PositiveInt


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

            def replace_env_var(match):
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


class ModelConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI models."""

    provider: str = Field(..., description="Model provider (e.g., azure_openai, openai)")
    id: str = Field(..., description="Model identifier")
    version: str = Field(..., description="Model version")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    params: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("params")
    def validate_params(cls, v):
        """Validate common model parameters."""
        if "temperature" in v:
            temp = v["temperature"]
            if not isinstance(temp, (int, float)) or not 0 <= temp <= 2:
                raise ValueError("Temperature must be between 0 and 2")

        if "max_tokens" in v:
            max_tokens = v["max_tokens"]
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                raise ValueError("max_tokens must be a positive integer")

        if "top_p" in v:
            top_p = v["top_p"]
            if not isinstance(top_p, (int, float)) or not 0 <= top_p <= 1:
                raise ValueError("top_p must be between 0 and 1")

        return v


class OpenAPIToolConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for OpenAPI tools."""

    schema_path: str = Field(..., description="Path to OpenAPI schema file")
    version: str = Field(..., description="Tool version")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP headers")
    base_url: Optional[str] = Field(None, description="Base URL for the API")
    timeout: Optional[PositiveInt] = Field(30, description="Request timeout in seconds")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("schema_path")
    def validate_schema_path(cls, v):
        """Validate that schema path exists."""
        if not v.startswith("/") and not v.startswith("tools/"):
            # Assume relative path from config directory
            v = f"tools/{v}" if not v.startswith("tools/") else v
        return v


class AIFoundryToolConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for Azure AI Foundry tools."""

    version: str = Field(..., description="Tool version")
    description: str = Field(..., description="Tool description")
    type: Optional[str] = Field(None, description="Tool type (e.g., bing, openapi)")
    schema_path: Optional[str] = Field(None, description="Path to schema file for OpenAPI tools")
    connection_ids: List[str] = Field(default_factory=list, description="Azure AI Foundry connection IDs")
    config: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific configuration")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("connection_ids")
    def validate_connection_ids(cls, v):
        """Ensure connection_ids is not empty for AI Foundry tools."""
        if not v:
            raise ValueError("At least one connection_id is required for AI Foundry tools")
        return v


class AIFoundryToolsConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for all Azure AI Foundry tools."""

    default_project_endpoint: str = Field(..., description="Default Azure AI Foundry project endpoint")
    tools: Dict[str, AIFoundryToolConfig] = Field(default_factory=dict, description="Individual tool configurations")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)


class ToolsConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for all tools."""

    openapi: Optional[Dict[str, OpenAPIToolConfig]] = Field(default_factory=dict, description="OpenAPI tools")
    ai_foundry: Optional[AIFoundryToolsConfig] = Field(None, description="Azure AI Foundry tools")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)


class SystemPromptConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for system prompts."""

    version: str = Field(..., description="Prompt version")
    path: str = Field(..., description="Path to prompt file")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("path")
    def validate_prompt_path(cls, v):
        """Validate that prompt path has correct extension."""
        if not v.endswith(".md") and not v.endswith(".txt"):
            raise ValueError("Prompt path must end with .md or .txt")
        return v


class AgentModelConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for agent model settings."""

    name: str = Field(..., description="Model name reference")
    temperature: Optional[PositiveFloat] = Field(None, description="Override temperature")
    max_tokens: Optional[PositiveInt] = Field(None, description="Override max tokens")
    top_p: Optional[PositiveFloat] = Field(None, description="Override top_p")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("temperature")
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if v is not None and not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v

    @validator("top_p")
    def validate_top_p(cls, v):
        """Validate top_p range."""
        if v is not None and not 0 <= v <= 1:
            raise ValueError("top_p must be between 0 and 1")
        return v


class AgentConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI agents."""

    version: str = Field(..., description="Agent version")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    model: AgentModelConfig = Field(..., description="Model configuration")
    tools: List[str] = Field(default_factory=list, description="List of tool references")
    platform: str = Field(..., description="Platform (e.g., azure_openai)")
    system_prompt: SystemPromptConfig = Field(..., description="System prompt configuration")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("tools")
    def validate_tools(cls, v):
        """Validate tool references format."""
        for tool in v:
            if not isinstance(tool, str):
                raise ValueError("Tool references must be strings")
            # Validate tool reference format (e.g., "ai_foundry.tools.bing")
            if "." not in tool:
                raise ValueError(f"Tool reference '{tool}' must be in format " "'category.subcategory.name'")
        return v


class AIConfig(BaseModel, EnvSubstitutionMixin):
    """Main AI configuration model."""

    version: str = Field(..., description="Configuration version")
    models: Dict[str, ModelConfig] = Field(default_factory=dict, description="Model configurations")
    tools: ToolsConfig = Field(default_factory=ToolsConfig, description="Tools configuration")
    agents: Dict[str, AgentConfig] = Field(default_factory=dict, description="Agent configurations")

    @root_validator(pre=True)
    def substitute_environment_variables(cls, values):
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @validator("agents")
    def validate_agent_model_references(cls, v, values):
        """Validate that agent model references exist in models config."""
        if "models" in values:
            available_models = set(values["models"].keys())
            for agent_name, agent_config in v.items():
                model_name = agent_config.model.name
                if model_name not in available_models:
                    raise ValueError(
                        f"Agent '{agent_name}' references unknown model " f"'{model_name}'. Available models: " f"{list(available_models)}"
                    )
        return v

    def validate_tool_references(self) -> None:
        """Validate that all agent tool references exist in tools config."""
        available_tools = set()

        # Collect available OpenAPI tools
        if self.tools.openapi:
            for tool_name in self.tools.openapi.keys():
                available_tools.add(f"openapi.{tool_name}")

        # Collect available AI Foundry tools
        if self.tools.ai_foundry and self.tools.ai_foundry.tools:
            for tool_name in self.tools.ai_foundry.tools.keys():
                available_tools.add(f"ai_foundry.tools.{tool_name}")

        # Validate agent tool references
        for agent_name, agent_config in self.agents.items():
            for tool_ref in agent_config.tools:
                if tool_ref not in available_tools:
                    raise ValueError(f"Agent '{agent_name}' references unknown tool " f"'{tool_ref}'. Available tools: " f"{list(available_tools)}")

    def get_resolved_config(self) -> "AIConfig":
        """
        Get a copy of the config with all environment variables resolved.

        Returns:
            A new AIConfig instance with resolved environment variables
        """
        # Since environment variable substitution happens during validation,
        # this returns self, but could be extended for additional processing
        return self


class ConfigLoader:
    """Utility class for loading and validating AI configurations."""

    @staticmethod
    def load_from_file(config_path: Union[str, Path]) -> AIConfig:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Validated AIConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        import yaml

        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        config = AIConfig(**raw_config)

        # Validate tool references after model creation
        config.validate_tool_references()

        return config

    @staticmethod
    def load_from_dict(config_dict: Dict[str, Any]) -> AIConfig:
        """
        Load configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Validated AIConfig instance
        """
        config = AIConfig(**config_dict)
        config.validate_tool_references()
        return config

    @staticmethod
    def validate_file_references(config: AIConfig, base_path: Union[str, Path]) -> List[str]:
        """
        Validate that all file references in the configuration exist.

        Args:
            config: The configuration to validate
            base_path: Base path for resolving relative file paths

        Returns:
            List of missing file paths
        """
        base_path = Path(base_path)
        missing_files = []

        # Check OpenAPI schema files
        if config.tools.openapi:
            for tool_name, tool_config in config.tools.openapi.items():
                schema_path = base_path / tool_config.schema_path
                if not schema_path.exists():
                    missing_files.append(str(schema_path))

        # Check AI Foundry schema files
        if config.tools.ai_foundry and config.tools.ai_foundry.tools:
            for tool_name, tool_config in config.tools.ai_foundry.tools.items():
                if tool_config.schema_path:
                    schema_path = base_path / tool_config.schema_path
                    if not schema_path.exists():
                        missing_files.append(str(schema_path))

        # Check prompt files
        for agent_name, agent_config in config.agents.items():
            prompt_path = base_path / agent_config.system_prompt.path
            if not prompt_path.exists():
                missing_files.append(str(prompt_path))

        return missing_files


# Example usage and validation functions
def validate_environment_variables(config: AIConfig) -> List[str]:
    """
    Check which environment variables are required but not set.

    Args:
        config: The configuration to check

    Returns:
        List of missing environment variable names
    """
    import re

    # Convert config to JSON to find all env variable references
    config_json = config.model_dump_json()

    # Find all ${env:VAR_NAME} patterns
    env_pattern = r"\$\{env:([^}]+)\}"
    env_vars = set(re.findall(env_pattern, config_json))

    # Check which ones are missing
    missing_vars = []
    for var in env_vars:
        if os.getenv(var) is None:
            missing_vars.append(var)

    return missing_vars


def create_example_config() -> Dict[str, Any]:
    """Create an example configuration dictionary for testing."""
    return {
        "version": "1.0",
        "models": {
            "standard-assistant": {
                "provider": "azure_openai",
                "id": "gpt-4-turbo",
                "version": "1.0",
                "config": {
                    "api_key": "${env:AZURE_OPENAI_KEY}",
                    "endpoint": "${env:AZURE_OPENAI_ENDPOINT}",
                    "deployment": "cdp-analysis-gpt-4o",
                    "api_version": "2023-12-01-preview",
                },
                "params": {"temperature": 0.2, "max_tokens": 4096, "top_p": 0.95},
            }
        },
        "tools": {
            "openapi": {
                "opoint": {
                    "schema_path": "tools/openapi/opoint.schema.json",
                    "version": "1.0",
                    "headers": {
                        "Authorization": "${env:OPENAPI_OPOINT_API_KEY}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                }
            },
            "ai_foundry": {
                "default_project_endpoint": "${env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}",
                "tools": {
                    "bing_search": {
                        "version": "1.0",
                        "type": "bing",
                        "description": "Bing web search tool via Azure AI Foundry agent connection",
                        "connection_ids": ["${env:BING_SEARCH_CONNECTION_ID}"],
                        "config": {"project_endpoint": "default_project_endpoint"},
                    }
                },
            },
        },
        "agents": {
            "sk-search-agent": {
                "version": "1.0",
                "name": "sk-search-agent",
                "description": "AI agent for performing web searches using Bing",
                "model": {"name": "standard-assistant", "temperature": 0.5},
                "tools": ["ai_foundry.tools.bing_search"],
                "platform": "azure_openai",
                "system_prompt": {
                    "version": "1.0",
                    "path": "prompts/search-agent.prompt.md",
                },
            }
        },
    }
