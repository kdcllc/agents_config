"""
Tool configuration classes.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt

from .base import EnvSubstitutionMixin


class OpenAPIToolConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for OpenAPI-based tools."""

    name: Optional[str] = Field(None, description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    schema_path: str = Field(..., description="Path to OpenAPI schema file")
    version: Optional[str] = Field(None, description="Tool version")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    base_url: Optional[str] = Field(None, description="Base URL for the API")
    timeout: Optional[PositiveInt] = Field(30, description="Request timeout in seconds")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @model_validator(mode="after")
    def set_default_name_description(self) -> "OpenAPIToolConfig":
        """Set default name and description if not provided."""
        if self.name is None:
            # Extract name from schema_path or use a default
            import os

            schema_name = os.path.splitext(os.path.basename(self.schema_path))[0]
            self.name = schema_name if schema_name else "openapi_tool"

        if self.description is None:
            self.description = f"OpenAPI tool: {self.name}"

        return self

    @field_validator("schema_path")
    @classmethod
    def validate_schema_path(cls, v: str) -> str:
        """Validate that schema path exists."""
        if not v.startswith("/") and not v.startswith("tools/"):
            # Assume relative path from config directory
            v = f"tools/{v}" if not v.startswith("tools/") else v
        return v


class AIFoundryToolConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI Foundry tools."""

    name: Optional[str] = Field(None, description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    version: Optional[str] = Field(None, description="Tool version")
    type: Optional[str] = Field(None, description="Tool type (e.g., bing, openapi)")
    schema_path: Optional[str] = Field(None, description="Path to schema file for openapi tools")
    container_name: Optional[str] = Field(None, description="Container name for the tool")
    connection_ids: Union[List[str], Dict[str, str]] = Field(default_factory=lambda: [], description="Connection IDs (list or dict)")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional configuration")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @model_validator(mode="after")
    def set_defaults_and_normalize(self) -> "AIFoundryToolConfig":
        """Set default values and normalize connection_ids format."""
        # Set default name if not provided
        if self.name is None:
            self.name = "ai_foundry_tool"

        # Set default description if not provided
        if self.description is None:
            self.description = f"AI Foundry tool: {self.name}"

        # Normalize connection_ids from list to dict if needed
        if isinstance(self.connection_ids, list):
            if len(self.connection_ids) == 1:
                # Single connection, use 'default' as key
                self.connection_ids = {"default": self.connection_ids[0]}
            else:
                # Multiple connections, use index-based keys
                self.connection_ids = {f"connection_{i}": conn_id for i, conn_id in enumerate(self.connection_ids)}

        return self

    @field_validator("connection_ids", mode="before")
    @classmethod
    def validate_connection_ids_input(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        """Validate connection IDs input format."""
        if isinstance(v, list):
            for item in v:
                if not isinstance(item, str):
                    raise ValueError("Connection IDs in list must be strings")
        elif isinstance(v, dict):
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError("Connection IDs must be string-to-string mappings")
        else:
            raise ValueError("Connection IDs must be a list or dictionary")
        return v


class AIFoundryToolsConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI Foundry tools collection."""

    default_project_endpoint: Optional[str] = Field(None, description="Default project endpoint for AI Foundry")
    tools: Dict[str, AIFoundryToolConfig] = Field(default_factory=dict, description="AI Foundry tools")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)


class ToolsConfig(BaseModel, EnvSubstitutionMixin):
    """Main tools configuration."""

    openapi: Dict[str, OpenAPIToolConfig] = Field(default_factory=dict, description="OpenAPI tools")
    ai_foundry: AIFoundryToolsConfig = Field(
        default_factory=lambda: AIFoundryToolsConfig(default_project_endpoint=None, tools={}),
        description="AI Foundry tools",
    )

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)
