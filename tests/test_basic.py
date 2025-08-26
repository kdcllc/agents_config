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
                "model": {"name": "base-model"},
                "platform": "${ref:models.base-model.provider}",
                "system_prompt": {"version": "1.0", "path": "test.md"},
            }
        },
        "tools": {},
    }

    config = ConfigLoader.load_from_dict(config_dict)

    # Verify reference was resolved in platform field
    assert config.agents["test-agent"].platform == "azure_openai"


if __name__ == "__main__":
    pytest.main([__file__])
