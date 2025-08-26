"""Basic tests for agents-config package."""

import pytest

from agents_config.ai_config import AIConfig
from agents_config.config_loader import ConfigLoader


def test_package_imports() -> None:
    """Test that core modules can be imported."""
    from agents_config import AIConfig, ConfigLoader
    from agents_config.agent_config import AgentConfig
    from agents_config.model_config import ModelConfig
    from agents_config.tool_config import ToolsConfig

    assert AIConfig is not None
    assert ConfigLoader is not None
    assert AgentConfig is not None
    assert ModelConfig is not None
    assert ToolsConfig is not None


def test_config_loader_basic() -> None:
    """Test basic ConfigLoader functionality."""
    # Test minimal config with required fields
    config = ConfigLoader.load_from_dict({"version": "1.0", "models": {}, "agents": {}, "tools": {}})

    assert isinstance(config, AIConfig)
    assert config.version == "1.0"
    assert config.models is not None
    assert config.agents is not None
    assert config.tools is not None


def test_environment_variable_substitution() -> None:
    """Test environment variable substitution."""
    import os

    # Set test environment variable
    os.environ["TEST_API_KEY"] = "test-key-123"

    config_dict = {
        "version": "1.0",
        "models": {"test-model": {"provider": "azure_openai", "id": "gpt-4", "version": "1.0", "config": {"api_key": "${env:TEST_API_KEY}"}}},
        "agents": {},
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)

    # Verify substitution occurred - access through config dict
    assert config.models["test-model"].config["api_key"] == "test-key-123"

    # Clean up
    del os.environ["TEST_API_KEY"]


def test_reference_resolution() -> None:
    """Test internal reference resolution."""
    config_dict = {
        "version": "1.0",
        "models": {
            "base-model": {
                "provider": "azure_openai",
                "id": "gpt-4",
                "version": "1.0",
                "config": {"api_key": "base-key", "endpoint": "https://test.openai.azure.com"},
            }
        },
        "agents": {
            "test-agent": {
                "version": "1.0",
                "name": "test-agent",
                "description": "Test agent",
                "model": "${ref:models.base-model}",
                "platform": "${ref:models.base-model.provider}",
                "system_prompt": {"version": "1.0", "path": "test.md"},
            }
        },
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)

    # Verify reference was resolved in platform field
    assert config.agents["test-agent"].platform == "azure_openai"
    
    # Verify model reference was resolved to actual ModelConfig object
    agent = config.agents["test-agent"]
    from agents_config.model_config import ModelConfig
    assert isinstance(agent.model, ModelConfig)
    assert agent.model.provider == "azure_openai"
    assert agent.model.id == "gpt-4"


def test_model_reference_resolution() -> None:
    """Test that model references are properly resolved to ModelConfig objects."""
    import os
    
    # Set required environment variables
    os.environ["TEST_API_KEY"] = "test-key-123"
    
    config_dict = {
        "version": "1.0",
        "models": {
            "test-model": {
                "provider": "azure_openai",
                "id": "gpt-4",
                "version": "1.0",
                "config": {
                    "api_key": "${env:TEST_API_KEY}",
                    "endpoint": "https://test.openai.azure.com",
                    "deployment": "test-deployment",
                },
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            }
        },
        "agents": {
            "test-agent": {
                "version": "1.0",
                "name": "test-agent",
                "description": "Test agent with model reference",
                "model": "${ref:models.test-model}",
                "platform": "azure_openai",
                "system_prompt": {"version": "1.0", "path": "test.md"},
                "tools": [],
            }
        },
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)
    
    # Verify agent has resolved model
    agent = config.agents["test-agent"]
    from agents_config.model_config import ModelConfig
    assert isinstance(agent.model, ModelConfig)
    
    # Test agent model access methods
    assert agent.get_model_provider() == "azure_openai"
    assert agent.get_model_id() == "gpt-4"
    assert agent.get_model_config()["api_key"] == "test-key-123"
    assert agent.get_model_params()["temperature"] == 0.7
    assert agent.get_model_params()["max_tokens"] == 1000
    
    # Clean up
    del os.environ["TEST_API_KEY"]


def test_agent_helper_methods() -> None:
    """Test helper methods on AgentConfig for accessing model and tools."""
    config_dict = {
        "version": "1.0",
        "models": {
            "helper-model": {
                "provider": "azure_openai",
                "id": "gpt-3.5-turbo",
                "version": "1.0",
                "config": {"api_key": "test-key", "endpoint": "https://test.openai.azure.com"},
                "params": {"temperature": 0.5},
            }
        },
        "agents": {
            "helper-agent": {
                "version": "1.0",
                "name": "helper-agent",
                "description": "Agent for testing helper methods",
                "model": "${ref:models.helper-model}",
                "platform": "azure_openai",
                "system_prompt": {"version": "1.0", "path": "test.md"},
                "tools": [],
            }
        },
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)
    agent = config.agents["helper-agent"]
    
    # Test model helper methods
    model = agent.get_resolved_model()
    assert model.provider == "azure_openai"
    assert model.id == "gpt-3.5-turbo"
    
    assert agent.get_model_provider() == "azure_openai"
    assert agent.get_model_id() == "gpt-3.5-turbo"
    
    model_config = agent.get_model_config()
    assert model_config["api_key"] == "test-key"
    
    model_params = agent.get_model_params()
    assert model_params["temperature"] == 0.5
    
    # Test tool helper methods
    tools = agent.get_resolved_tools()
    assert len(tools) == 0
    
    assert agent.get_tool_count() == 0
    assert agent.get_tool_names() == []


def test_invalid_model_reference() -> None:
    """Test that invalid model references raise appropriate errors."""
    config_dict = {
        "version": "1.0",
        "models": {
            "valid-model": {
                "provider": "azure_openai",
                "id": "gpt-4",
                "version": "1.0",
                "config": {"api_key": "test-key"},
            }
        },
        "agents": {
            "invalid-agent": {
                "version": "1.0",
                "name": "invalid-agent",
                "description": "Agent with invalid model reference",
                "model": "${ref:models.nonexistent-model}",
                "platform": "azure_openai",
                "system_prompt": {"version": "1.0", "path": "test.md"},
                "tools": [],
            }
        },
        "tools": {},
    }

    # Should raise ValueError for nonexistent model reference
    with pytest.raises(ValueError, match="Reference path .* not found"):
        ConfigLoader.load_from_dict(config_dict)


if __name__ == "__main__":
    pytest.main([__file__])
