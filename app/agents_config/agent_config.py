"""
Agent configuration classes.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveFloat, PositiveInt

from .base import EnvSubstitutionMixin


class SystemPromptConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for system prompts."""

    version: str = Field(..., description="Prompt version")
    path: str = Field(..., description="Path to prompt file")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("path")
    @classmethod
    def validate_prompt_path(cls, v: str) -> str:
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

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """Validate temperature range."""
        if v is not None and not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v

    @field_validator("top_p")
    @classmethod
    def validate_top_p(cls, v: Optional[float]) -> Optional[float]:
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

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("tools")
    @classmethod
    def validate_tools(cls, v: List[str]) -> List[str]:
        """Validate tool references format."""
        for tool in v:
            if not isinstance(tool, str):
                raise ValueError("Tool references must be strings")
            # Validate tool reference format (e.g., "ai_foundry.tools.bing")
            if "." not in tool:
                raise ValueError(f"Tool reference '{tool}' must be in format " "'category.subcategory.name'")
        return v
