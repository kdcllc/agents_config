"""
Main AI configuration class.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from .agent_config import AgentConfig
from .base import EnvSubstitutionMixin
from .model_config import ModelConfig
from .tool_config import ToolsConfig, OpenAPIToolConfig, AIFoundryToolConfig


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

            # Check tool references - tools are now objects, so validation is different
            if agent_config.tools:
                for tool in agent_config.tools:
                    # Tools are now actual configuration objects
                    # Validation happens during tool object creation
                    # We can add specific validation here if needed
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

    def get_tool(self, tool_ref: str) -> Optional[Union[OpenAPIToolConfig, AIFoundryToolConfig]]:
        """
        Get a tool configuration by its reference string.
        
        Args:
            tool_ref: Tool reference string (e.g., "ai_foundry.tools.bing_search", "openapi.weather")
            
        Returns:
            The tool configuration object or None if not found
        """
        if not isinstance(tool_ref, str) or "." not in tool_ref:
            return None
            
        parts = tool_ref.split(".")
        
        if len(parts) == 2 and parts[0] == "openapi":
            # OpenAPI tool: "openapi.tool_name"
            tool_name = parts[1]
            return self.tools.openapi.get(tool_name) if self.tools.openapi else None
            
        elif len(parts) == 3 and parts[0] == "ai_foundry" and parts[1] == "tools":
            # AI Foundry tool: "ai_foundry.tools.tool_name"
            tool_name = parts[2]
            if self.tools.ai_foundry and self.tools.ai_foundry.tools:
                return self.tools.ai_foundry.tools.get(tool_name)
            return None
            
        return None

    def get_agent_tools(self, agent_name: str) -> List[Union[OpenAPIToolConfig, AIFoundryToolConfig]]:
        """
        Get resolved tool configurations for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of tool configuration objects
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return []
            
        # Tools are now already resolved objects in the agent
        return agent.tools

    def list_models(self) -> List[str]:
        """List all available model names."""
        return list(self.models.keys())

    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return list(self.agents.keys())
