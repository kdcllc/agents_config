"""Basic tests for agents-config package."""

import pytest
from app.agents_config.config_loader import ConfigLoader
from app.agents_config.ai_config import AIConfig


def test_package_imports():
    """Test that core modules can be imported."""
    from app.agents_config import AIConfig, ConfigLoader
    from app.agents_config.agent_config import AgentConfig
    from app.agents_config.model_config import ModelConfig
    from app.agents_config.tool_config import ToolsConfig

    assert AIConfig is not None
    assert ConfigLoader is not None
    assert AgentConfig is not None
    assert ModelConfig is not None
    assert ToolsConfig is not None


def test_config_loader_basic():
    """Test basic ConfigLoader functionality."""
    # Test empty config
    config = ConfigLoader.load_from_dict({"models": {}, "agents": {}, "tools": {}})

    assert isinstance(config, AIConfig)
    assert config.models is not None
    assert config.agents is not None
    assert config.tools is not None


def test_environment_variable_substitution():
    """Test environment variable substitution."""
    import os

    # Set test environment variable
    os.environ["TEST_API_KEY"] = "test-key-123"

    config_dict = {
        "models": {
            "test-model": {"api_key": "${env:TEST_API_KEY}", "model_name": "gpt-4"}
        },
        "agents": {},
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)

    # Verify substitution occurred
    assert config.models["test-model"].api_key == "test-key-123"

    # Clean up
    del os.environ["TEST_API_KEY"]


def test_reference_resolution():
    """Test internal reference resolution."""
    config_dict = {
        "models": {"base-model": {"api_key": "base-key", "model_name": "gpt-4"}},
        "agents": {
            "test-agent": {
                "model": "${ref:models.base-model.model_name}",
                "description": "Test agent",
            }
        },
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)

    # Verify reference was resolved
    assert config.agents["test-agent"].model == "gpt-4"


if __name__ == "__main__":
    pytest.main([__file__])
