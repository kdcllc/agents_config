"""
Tests for the new model reference format in agents configuration.
"""

import os
import pytest
from agents_config.config_loader import ConfigLoader
from agents_config.agent_config import AgentConfig
from agents_config.model_config import ModelConfig


class TestModelReferences:
    """Test cases for the new model reference format."""

    def test_model_reference_format(self):
        """Test that agents can reference models using ${ref:models.model-name} format."""
        config_dict = {
            "version": "1.0",
            "models": {
                "gpt-4-model": {
                    "provider": "azure_openai",
                    "id": "gpt-4",
                    "version": "1.0",
                    "config": {"api_key": "test-key", "endpoint": "https://test.openai.azure.com"},
                    "params": {"temperature": 0.7, "max_tokens": 2000},
                }
            },
            "agents": {
                "test-agent": {
                    "version": "1.0",
                    "name": "test-agent",
                    "description": "Test agent with model reference",
                    "model": "${ref:models.gpt-4-model}",
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "test.md"},
                    "tools": [],
                }
            },
            "tools": {},
        }

        config = ConfigLoader.load_from_dict(config_dict)
        agent = config.agents["test-agent"]

        # Verify the model is resolved to a ModelConfig object
        assert isinstance(agent.model, ModelConfig)
        assert agent.model.provider == "azure_openai"
        assert agent.model.id == "gpt-4"
        assert agent.model.params["temperature"] == 0.7

    def test_agent_model_helper_methods(self):
        """Test the new helper methods for accessing model information."""
        config_dict = {
            "version": "1.0",
            "models": {
                "test-model": {
                    "provider": "azure_openai",
                    "id": "gpt-3.5-turbo",
                    "version": "1.0",
                    "config": {
                        "api_key": "secret-key",
                        "endpoint": "https://my-endpoint.com",
                        "deployment": "my-deployment",
                    },
                    "params": {"temperature": 0.5, "max_tokens": 1500, "top_p": 0.9},
                }
            },
            "agents": {
                "helper-agent": {
                    "version": "1.0",
                    "name": "helper-agent",
                    "description": "Agent for testing helper methods",
                    "model": "${ref:models.test-model}",
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "test.md"},
                    "tools": [],
                }
            },
            "tools": {},
        }

        config = ConfigLoader.load_from_dict(config_dict)
        agent = config.agents["helper-agent"]

        # Test all helper methods
        assert agent.get_model_provider() == "azure_openai"
        assert agent.get_model_id() == "gpt-3.5-turbo"

        model_config = agent.get_model_config()
        assert model_config["api_key"] == "secret-key"
        assert model_config["endpoint"] == "https://my-endpoint.com"
        assert model_config["deployment"] == "my-deployment"

        model_params = agent.get_model_params()
        assert model_params["temperature"] == 0.5
        assert model_params["max_tokens"] == 1500
        assert model_params["top_p"] == 0.9

        # Test get_resolved_model returns the same object
        resolved = agent.get_resolved_model()
        assert resolved is agent.model
        assert isinstance(resolved, ModelConfig)

    def test_multiple_agents_shared_model(self):
        """Test that multiple agents can reference the same model."""
        config_dict = {
            "version": "1.0",
            "models": {
                "shared-model": {
                    "provider": "azure_openai",
                    "id": "gpt-4",
                    "version": "1.0",
                    "config": {"api_key": "shared-key"},
                    "params": {"temperature": 0.3},
                }
            },
            "agents": {
                "agent1": {
                    "version": "1.0",
                    "name": "agent1",
                    "description": "First agent",
                    "model": "${ref:models.shared-model}",
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "agent1.md"},
                    "tools": [],
                },
                "agent2": {
                    "version": "1.0",
                    "name": "agent2",
                    "description": "Second agent",
                    "model": "${ref:models.shared-model}",
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "agent2.md"},
                    "tools": [],
                },
            },
            "tools": {},
        }

        config = ConfigLoader.load_from_dict(config_dict)

        agent1 = config.agents["agent1"]
        agent2 = config.agents["agent2"]

        # Both agents should have resolved ModelConfig objects
        assert isinstance(agent1.model, ModelConfig)
        assert isinstance(agent2.model, ModelConfig)

        # Both should reference the same model configuration
        assert agent1.get_model_id() == agent2.get_model_id() == "gpt-4"
        assert agent1.get_model_provider() == agent2.get_model_provider() == "azure_openai"
        assert agent1.get_model_params()["temperature"] == agent2.get_model_params()["temperature"] == 0.3

    def test_invalid_model_reference(self):
        """Test that invalid model references raise proper errors."""
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

    def test_environment_variable_substitution_in_model_references(self):
        """Test that environment variables work correctly in model configurations."""
        # Set test environment variable
        os.environ["TEST_MODEL_API_KEY"] = "env-test-key-456"

        try:
            config_dict = {
                "version": "1.0",
                "models": {
                    "env-model": {
                        "provider": "azure_openai",
                        "id": "gpt-4",
                        "version": "1.0",
                        "config": {
                            "api_key": "${env:TEST_MODEL_API_KEY}",
                            "endpoint": "https://test.openai.azure.com",
                        },
                        "params": {"temperature": 0.8},
                    }
                },
                "agents": {
                    "env-agent": {
                        "version": "1.0",
                        "name": "env-agent",
                        "description": "Agent with environment variable in model",
                        "model": "${ref:models.env-model}",
                        "platform": "azure_openai",
                        "system_prompt": {"version": "1.0", "path": "test.md"},
                        "tools": [],
                    }
                },
                "tools": {},
            }

            config = ConfigLoader.load_from_dict(config_dict)
            agent = config.agents["env-agent"]

            # Verify environment variable was substituted
            assert agent.get_model_config()["api_key"] == "env-test-key-456"
            assert agent.get_model_params()["temperature"] == 0.8

        finally:
            # Clean up environment variable
            del os.environ["TEST_MODEL_API_KEY"]

    def test_backward_incompatibility(self):
        """Test that old model format is rejected."""
        config_dict = {
            "version": "1.0",
            "models": {
                "test-model": {
                    "provider": "azure_openai",
                    "id": "gpt-4",
                    "version": "1.0",
                    "config": {"api_key": "test-key"},
                }
            },
            "agents": {
                "old-format-agent": {
                    "version": "1.0",
                    "name": "old-format-agent",
                    "description": "Agent using old model format",
                    "model": {"name": "test-model", "temperature": 0.5},  # Old format
                    "platform": "azure_openai",
                    "system_prompt": {"version": "1.0", "path": "test.md"},
                    "tools": [],
                }
            },
            "tools": {},
        }

        # Should raise validation error for old format
        with pytest.raises(ValueError, match="Configuration validation failed"):
            ConfigLoader.load_from_dict(config_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])