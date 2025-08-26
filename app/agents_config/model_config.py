"""
Model configuration classes.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import EnvSubstitutionMixin


class ModelConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI models."""

    provider: str = Field(..., description="Model provider (e.g., azure_openai, openai)")
    id: str = Field(..., description="Model identifier")
    version: str = Field(..., description="Model version")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    params: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("params")
    @classmethod
    def validate_params(cls, v: Dict[str, Any]) -> Dict[str, Any]:
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
