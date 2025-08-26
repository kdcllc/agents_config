"""
Agent configuration classes.
"""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveFloat, PositiveInt

from .base import EnvSubstitutionMixin

if TYPE_CHECKING:
    from .tool_config import OpenAPIToolConfig, AIFoundryToolConfig
    from .model_config import ModelConfig


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


class AgentConfig(BaseModel, EnvSubstitutionMixin):
    """Configuration for AI agents."""

    version: str = Field(..., description="Agent version")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    model: Union[str, "ModelConfig"] = Field(..., description="Model reference or configuration")
    tools: List[Union["OpenAPIToolConfig", "AIFoundryToolConfig"]] = Field(
        default_factory=list, 
        description="List of tool configuration objects"
    )
    platform: str = Field(..., description="Platform (e.g., azure_openai)")
    system_prompt: SystemPromptConfig = Field(..., description="System prompt configuration")

    @model_validator(mode="before")
    @classmethod
    def substitute_environment_variables(cls, values: Any) -> Any:
        """Substitute environment variables in all string fields."""
        return cls.substitute_env_vars(values)

    @field_validator("tools", mode="before")
    @classmethod
    def validate_tools(cls, v: List[Union[str, dict, Any]]) -> List[Union[str, dict]]:
        """Pre-validate tools - accept strings or dicts for later conversion."""
        if not isinstance(v, list):
            raise ValueError("Tools must be a list")
            
        validated_tools = []
        for tool in v:
            if isinstance(tool, str):
                # Tool reference string - validate format
                if "." not in tool:
                    raise ValueError(f"Tool reference '{tool}' must be in format 'category.subcategory.name'")
                validated_tools.append(tool)
            elif isinstance(tool, dict):
                # Tool configuration dictionary
                validated_tools.append(tool)
            else:
                # Assume it's already a tool configuration object
                validated_tools.append(tool)
                
        return validated_tools

    @model_validator(mode="after")
    def validate_model_reference(self) -> "AgentConfig":
        """Validate that model is properly resolved."""
        from .model_config import ModelConfig
        
        if isinstance(self.model, str):
            raise ValueError(f"Model reference '{self.model}' was not resolved to a ModelConfig object")
        elif not isinstance(self.model, ModelConfig):
            raise ValueError(f"Model must be a ModelConfig object, got {type(self.model)}")
            
        return self

    @model_validator(mode="after")
    def convert_tools_to_objects(self) -> "AgentConfig":
        """Convert tool references and dictionaries to actual tool configuration objects."""
        from .tool_config import OpenAPIToolConfig, AIFoundryToolConfig
        
        converted_tools = []
        for tool in self.tools:
            if isinstance(tool, str):
                # This should not happen if references are resolved properly
                raise ValueError(f"Tool reference '{tool}' was not resolved to a configuration object")
            elif isinstance(tool, dict):
                # Convert dictionary to appropriate tool configuration object
                if "schema_path" in tool and "type" not in tool:
                    # Looks like OpenAPI tool
                    converted_tools.append(OpenAPIToolConfig(**tool))
                else:
                    # Assume AI Foundry tool
                    converted_tools.append(AIFoundryToolConfig(**tool))
            elif isinstance(tool, (OpenAPIToolConfig, AIFoundryToolConfig)):
                # Already a valid tool configuration object
                converted_tools.append(tool)
            else:
                raise ValueError(f"Tool must be a configuration object or dictionary, got {type(tool)}")
                
        self.tools = converted_tools
        return self

    def get_resolved_model(self) -> "ModelConfig":
        """
        Get the resolved model configuration for this agent.
        
        Returns:
            The ModelConfig object for this agent
        """
        from .model_config import ModelConfig
        
        if not isinstance(self.model, ModelConfig):
            raise ValueError(f"Model is not resolved. Expected ModelConfig, got {type(self.model)}")
        
        return self.model

    def get_model_provider(self) -> str:
        """
        Get the model provider from the resolved model configuration.
        
        Returns:
            The provider string (e.g., "azure_openai")
        """
        model_config = self.get_resolved_model()
        return model_config.provider

    def get_model_id(self) -> str:
        """
        Get the model ID from the resolved model configuration.
        
        Returns:
            The model ID string (e.g., "gpt-4-turbo")
        """
        model_config = self.get_resolved_model()
        return model_config.id

    def get_model_config(self) -> Dict[str, Any]:
        """
        Get the model configuration dictionary.
        
        Returns:
            The model config dictionary with API keys, endpoints, etc.
        """
        model_config = self.get_resolved_model()
        return model_config.config

    def get_model_params(self) -> Dict[str, Any]:
        """
        Get the model parameters dictionary.
        
        Returns:
            The model params dictionary with temperature, max_tokens, etc.
        """
        model_config = self.get_resolved_model()
        return model_config.params if model_config.params else {}

    def get_resolved_tools(self) -> List[Union["OpenAPIToolConfig", "AIFoundryToolConfig"]]:
        """
        Get resolved tool configurations for this agent.
        
        Returns:
            List of tool configuration objects (OpenAPIToolConfig or AIFoundryToolConfig)
        """
        # Tools are now already resolved objects
        return self.tools

    def get_tool(self, tool_name: str) -> Optional[Union["OpenAPIToolConfig", "AIFoundryToolConfig"]]:
        """
        Get a specific tool configuration by name.
        
        Args:
            tool_name: Tool name to search for
            
        Returns:
            The tool configuration object or None if not found
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if this agent has a specific tool by name.
        
        Args:
            tool_name: Tool name to search for
            
        Returns:
            True if the agent has this tool, False otherwise
        """
        return self.get_tool(tool_name) is not None

    def get_tool_count(self) -> int:
        """
        Get the number of tools configured for this agent.
        
        Returns:
            Number of tools
        """
        return len(self.tools)

    def get_tool_names(self) -> List[str]:
        """
        Get the names of all tools configured for this agent.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools if tool.name]

    def has_tool_type(self, tool_type: str) -> bool:
        """
        Check if this agent has any tools of a specific type.
        
        Args:
            tool_type: Type to check for ("openapi" or "ai_foundry")
            
        Returns:
            True if the agent has tools of this type, False otherwise
        """
        from .tool_config import OpenAPIToolConfig, AIFoundryToolConfig
        
        if tool_type == "openapi":
            return any(isinstance(tool, OpenAPIToolConfig) for tool in self.tools)
        elif tool_type == "ai_foundry":
            return any(isinstance(tool, AIFoundryToolConfig) for tool in self.tools)
        else:
            return False

    def get_tools_by_type(self, tool_type: str) -> List[Union["OpenAPIToolConfig", "AIFoundryToolConfig"]]:
        """
        Get all tools of a specific type.
        
        Args:
            tool_type: Type to filter by ("openapi" or "ai_foundry")
            
        Returns:
            List of tool configuration objects of the specified type
        """
        from .tool_config import OpenAPIToolConfig, AIFoundryToolConfig
        
        if tool_type == "openapi":
            return [tool for tool in self.tools if isinstance(tool, OpenAPIToolConfig)]
        elif tool_type == "ai_foundry":
            return [tool for tool in self.tools if isinstance(tool, AIFoundryToolConfig)]
        else:
            return []
