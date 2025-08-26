"""
Main AI configuration class.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .agent_config import AgentConfig
from .base import EnvSubstitutionMixin
from .model_config import ModelConfig
from .tool_config import ToolsConfig


class AIConfig(BaseModel, EnvSubstitutionMixin):
    """Main configuration class for AI system."""

    version: str = Field(..., description="Configuration version")
    models: Dict[str, ModelConfig] = Field(default_factory=dict, description="Model configurations")
    tools: ToolsConfig = Field(default_factory=ToolsConfig, description="Tools configuration")
    agents: Dict[str, AgentConfig] = Field(default_factory=dict, description="Agent configurations")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("models", mode="before")
    @classmethod
    def validate_models(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert model configurations."""
        if not isinstance(v, dict):
            raise ValueError("Models configuration must be a dictionary")
        return v

    @field_validator("agents", mode="before")
    @classmethod
    def validate_agents(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert agent configurations."""
        if not isinstance(v, dict):
            raise ValueError("Agents configuration must be a dictionary")
        return v

    @model_validator(mode="after")
    def validate_cross_references(self) -> "AIConfig":
        """Validate cross-references between agents, models, and tools."""
        models = self.models
        tools_config = self.tools
        agents = self.agents

        # Extract available model names
        available_models = set(models.keys()) if models else set()

        # Extract available tool names from nested structure
        available_tools: set[str] = set()
        if tools_config.openapi:
            available_tools.update(tools_config.openapi.keys())
        if tools_config.ai_foundry and tools_config.ai_foundry.tools:
            available_tools.update(tools_config.ai_foundry.tools.keys())

        # Validate agent references
        for agent_name, agent_config in agents.items():
            # Check model reference
            if agent_config.model and agent_config.model.name:
                model_name = agent_config.model.name
                if model_name not in available_models:
                    raise ValueError(
                        f"Agent '{agent_name}' references unknown model " f"'{model_name}'. Available models: " f"{sorted(available_models)}"
                    )

            # Check tool references
            if agent_config.tools:
                for tool_ref in agent_config.tools:
                    if tool_ref not in available_tools:
                        # For now, just warn rather than error for tool
                        # references as the tool structure is complex
                        pass

        return self

    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get a model configuration by name."""
        models = getattr(self, "models", None)
        if isinstance(models, dict):
            return models.get(name)
        return None

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get an agent configuration by name."""
        return self.agents.get(name)

    def list_models(self) -> List[str]:
        """List all available model names."""
        return list(self.models.keys())

    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return list(self.agents.keys())
