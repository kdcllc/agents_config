# AI Agents Configuration Library

![I stand with Israel](./images/IStandWithIsrael.png)

A robust Python library for managing AI agent configurations with **Pydantic validation**, **environment variable substitution**, and **internal reference resolution**. Perfect for building scalable AI applications with complex tool integrations and deployment flexibility.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic V2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Hire Me

Please send [email](mailto:kingdavidconsulting@gmail.com) if you consider hiring me.

[![buymeacoffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/vyve0og)

## Give a Star! :star:

If you like or are using this project to learn or start your solution, please give it a star. Thanks!

## 🚀 Quick Start

### Installation

```bash
# Install with uv (recommended)
uv add agents-config

# Or with pip
pip install agents-config

# Install development version from GitHub
pip install git+https://github.com/kdcllc/agents_config.git

# For development work
git clone https://github.com/kdcllc/agents_config.git
cd agents_config
uv sync --all-extras
```

### Basic Usage

```python
from agents_config.config_loader import ConfigLoader

# Load configuration from YAML file
config = ConfigLoader.load_from_file("ai-config.yaml")

# Access models, agents, and tools
model = config.get_model("gpt-4")
agent = config.get_agent("search-agent")
print(f"Agent: {agent.description}")
```

### Run the Demo

```bash
# See the library in action
uv run main.py

# Or with python
python main.py
```

## 🎯 Key Features

- **🔧 Pydantic V2 Validation**: Type-safe configuration with automatic validation
- **🌍 Environment Variables**: `${env:VAR_NAME}` substitution for secrets and deployment configs
- **🔗 Internal References**: `${ref:path.to.value}` resolution for DRY configurations
- **🛠️ Multi-Tool Support**: OpenAPI tools, Azure AI Foundry agents, custom integrations
- **📦 Flexible Models**: Support for Azure OpenAI, OpenAI, Ollama, and custom providers
- **✅ Cross-Reference Validation**: Ensures agents reference valid models and tools
- **🔄 Programmatic Configuration**: Create configs in code or load from YAML

## 📖 Configuration Structure

### YAML Configuration Example

```yaml
version: '1.0'

# Models define AI providers and their configurations
models:
  gpt-4:
    provider: azure_openai
    id: gpt-4-turbo
    version: '1.0'
    config:
      api_key: ${env:AZURE_OPENAI_KEY}
      endpoint: ${env:AZURE_OPENAI_ENDPOINT}
      deployment: my-deployment
    params:
      temperature: 0.7
      max_tokens: 4096

# Tools define external integrations
tools:
  ai_foundry:
    default_project_endpoint: ${env:AZURE_AI_FOUNDRY_ENDPOINT}
    tools:
      search_tool:
        version: '1.0'
        type: bing
        description: 'Web search via Azure AI Foundry'
        connection_ids:
          - ${env:BING_CONNECTION_ID}
        config:
          project_endpoint: ${ref:tools.ai_foundry.default_project_endpoint}

# Agents combine models and tools for specific tasks
agents:
  search-agent:
    version: '1.0'
    name: 'Search Agent'
    description: 'AI agent for web searches'
    model:
      name: gpt-4
      temperature: 0.5
    tools:
      - ${ref:tools.ai_foundry.tools.search_tool}
    platform: azure_openai
    system_prompt:
      version: '1.0'
      path: prompts/search-agent.md
```

## 🔧 Core Components

### 1. ConfigLoader

The main entry point for loading and validating configurations.

```python
from agents_config.config_loader import ConfigLoader

# Load from YAML file
config = ConfigLoader.load_from_file("config.yaml")

# Load from dictionary
config_dict = {"version": "1.0", "models": {...}}
config = ConfigLoader.load_from_dict(config_dict)

# Validate environment variables
missing_vars = ConfigLoader.validate_environment_variables(config)
if missing_vars:
    print(f"Missing environment variables: {missing_vars}")

# Create example configuration
ConfigLoader.save_example_config("example-config.yaml")
```

### 2. Environment Variable Substitution

Automatically resolves `${env:VAR_NAME}` patterns in your configuration:

```yaml
models:
  gpt-4:
    config:
      api_key: ${env:AZURE_OPENAI_KEY} # → Resolves to actual API key
      endpoint: ${env:AZURE_OPENAI_ENDPOINT} # → Resolves to actual endpoint
```

```python
import os
os.environ["AZURE_OPENAI_KEY"] = "your-api-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-endpoint.com"

config = ConfigLoader.load_from_file("config.yaml")
# Environment variables are automatically resolved
```

### 3. Internal Reference Resolution

Use `${ref:path.to.value}` to reference other parts of your configuration:

```yaml
shared_config:
  database_url: 'postgresql://localhost:5432/mydb'
  timeout: 30

models:
  gpt-4:
    config:
      database_url: ${ref:shared_config.database_url} # → References shared value
      timeout: ${ref:shared_config.timeout} # → References shared value
```

### 4. Working with Models

```python
# Get all available models
model_names = config.list_models()

# Get specific model
model = config.get_model("gpt-4")
if model:
    print(f"Provider: {model.provider}")
    print(f"ID: {model.id}")
    print(f"Config: {model.config}")
    print(f"Parameters: {model.params}")
```

### 5. Working with Agents

```python
# Get all available agents
agent_names = config.list_agents()

# Get specific agent
agent = config.get_agent("search-agent")
if agent:
    print(f"Name: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Model: {agent.model.name}")
    print(f"Tools: {agent.tools}")
    print(f"System Prompt: {agent.system_prompt.path}")
```

### 6. Tool Configuration

#### OpenAPI Tools

```yaml
tools:
  openapi:
    weather_api:
      schema_path: 'tools/openapi/weather.json'
      version: '1.0'
      headers:
        Authorization: ${env:WEATHER_API_KEY}
        Content-Type: 'application/json'
```

#### Azure AI Foundry Tools

```yaml
tools:
  ai_foundry:
    default_project_endpoint: ${env:AZURE_AI_FOUNDRY_ENDPOINT}
    tools:
      bing_search:
        version: '1.0'
        type: bing
        description: 'Bing search integration'
        connection_ids:
          - ${env:BING_CONNECTION_ID}
        config:
          project_endpoint: ${ref:tools.ai_foundry.default_project_endpoint}
```

## 🏗️ Programmatic Configuration

Create configurations in code for dynamic setups:

```python
from agents_config.ai_config import AIConfig
from agents_config.model_config import ModelConfig
from agents_config.agent_config import AgentConfig

# Create model configuration
model = ModelConfig(
    provider="azure_openai",
    id="gpt-4",
    version="1.0",
    config={
        "api_key": "your-api-key",
        "endpoint": "https://your-endpoint.com",
        "deployment": "gpt-4-deployment"
    },
    params={
        "temperature": 0.7,
        "max_tokens": 4000
    }
)

# Create agent configuration
agent = AgentConfig(
    version="1.0",
    name="My Agent",
    description="A programmatically created agent",
    model={"name": "gpt-4", "temperature": 0.5},
    tools=[],
    platform="azure_openai",
    system_prompt={
        "version": "1.0",
        "path": "prompts/my-agent.md"
    }
)

# Create full configuration
config = AIConfig(
    version="1.0",
    models={"gpt-4": model},
    tools={},
    agents={"my-agent": agent}
)
```

## 🔍 Validation and Error Handling

The library provides comprehensive validation with clear error messages:

```python
try:
    config = ConfigLoader.load_from_file("config.yaml")
except ValueError as e:
    print(f"Configuration validation failed: {e}")
    # Shows detailed validation errors:
    # - Missing required fields
    # - Invalid data types
    # - Cross-reference validation failures
```

Example validation error output:

```
Configuration validation failed: 6 validation errors for AIConfig
models.gpt-4.version
  Field required [type=missing, input_value={'provider': 'azure_openai'...}, input_type=dict]
models.gpt-4.config
  Input should be a valid dictionary [type=dict_type, input_value='not_a_dict', input_type=str]
agents.my-agent.system_prompt
  Field required [type=missing, input_value={'name': 'My Agent'...}, input_type=dict]
```

## 🌍 Environment Variables

### Required Environment Variables

Set these environment variables for the example configuration:

```bash
# Azure OpenAI
export AZURE_OPENAI_KEY="your-azure-openai-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Azure AI Foundry
export AZURE_AI_FOUNDRY_PROJECT_ENDPOINT="https://your-project.azure.ai/"

# Tool Connections
export BING_SEARCH_CONNECTION_ID="your-bing-connection-id"
export OPOINT_API_CONNECTION_ID="your-opoint-connection-id"
export OPENAPI_OPOINT_API_KEY="your-opoint-api-key"
```

### Environment Variable Validation

```python
# Check for missing environment variables before deployment
missing_vars = ConfigLoader.validate_environment_variables(config)
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
```

## 📁 Project Structure

agents-config/
├── app/
│ ├── agents_config/ # Main library package
│ │ ├── **init**.py
│ │ ├── ai_config.py # Main configuration class
│ │ ├── agent_config.py # Agent configuration models
│ │ ├── base.py # Base mixins for env/ref resolution
│ │ ├── config_loader.py # Configuration loading utilities
│ │ ├── config_models.py # Common configuration models
│ │ ├── model_config.py # AI model configuration
│ │ └── tool_config.py # Tool configuration models
│ └── ai-config/ # Example configuration
│ ├── ai-config.yaml # Main configuration file
│ ├── prompts/ # System prompt templates
│ └── tools/ # Tool schema definitions
├── main.py # Demo script
├── pyproject.toml # Project configuration
└── README.md # This file

````text

## 🛠️ Advanced Usage

### Custom Tool Integration

```python
from agents_config.tool_config import ToolsConfig

# Define custom tools
custom_tools = ToolsConfig(
    openapi={
        "my_api": {
            "schema_path": "tools/my_api.json",
            "version": "1.0",
            "headers": {
                "Authorization": "${env:MY_API_KEY}"
            }
        }
    }
)
````

### Multi-Environment Configuration

```yaml
# config/production.yaml
version: '1.0'
models:
  gpt-4:
    config:
      endpoint: ${env:PROD_OPENAI_ENDPOINT}
      api_key: ${env:PROD_OPENAI_KEY}

# config/development.yaml
version: '1.0'
models:
  gpt-4:
    config:
      endpoint: ${env:DEV_OPENAI_ENDPOINT}
      api_key: ${env:DEV_OPENAI_KEY}
```

```python
import os

# Load environment-specific configuration
env = os.getenv("ENVIRONMENT", "development")
config_path = f"config/{env}.yaml"
config = ConfigLoader.load_from_file(config_path)
```

### Configuration Composition

```python
# Base configuration
base_config = ConfigLoader.load_from_file("base-config.yaml")

# Environment-specific overrides
env_config = ConfigLoader.load_from_file(f"config/{env}.yaml")

# Merge configurations (implement your merge logic)
final_config = merge_configurations(base_config, env_config)
```

## 🧪 Testing

```python
import pytest
from agents_config.config_loader import ConfigLoader

def test_configuration_loading():
    """Test that configuration loads successfully."""
    config = ConfigLoader.load_from_file("test-config.yaml")
    assert config.version == "1.0"
    assert "gpt-4" in config.models
    assert len(config.agents) > 0

def test_environment_variable_substitution():
    """Test environment variable resolution."""
    import os
    os.environ["TEST_API_KEY"] = "test-key-123"

    config_dict = {
        "version": "1.0",
        "models": {
            "test-model": {
                "provider": "azure_openai",
                "config": {"api_key": "${env:TEST_API_KEY}"}
            }
        }
    }

    config = ConfigLoader.load_from_dict(config_dict)
    model = config.get_model("test-model")
    assert model.config["api_key"] == "test-key-123"
```

## 🚀 Deployment

### Docker Integration

```dockerfile
FROM python:3.12-slim

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy configuration
COPY config/ /app/config/
COPY prompts/ /app/prompts/

# Set environment variables
ENV ENVIRONMENT=production
ENV AZURE_OPENAI_ENDPOINT=https://your-endpoint.com

# Run your application
CMD ["python", "your_app.py"]
```

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-config
data:
  ai-config.yaml: |
    version: '1.0'
    models:
      gpt-4:
        provider: azure_openai
        config:
          endpoint: ${env:AZURE_OPENAI_ENDPOINT}
          api_key: ${env:AZURE_OPENAI_KEY}
---
apiVersion: v1
kind: Secret
metadata:
  name: ai-secrets
data:
  AZURE_OPENAI_KEY: <base64-encoded-key>
  AZURE_OPENAI_ENDPOINT: <base64-encoded-endpoint>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/kdcllc/agents_config/issues)
- **Documentation**: This README and inline code documentation
- **Examples**: See `main.py` for comprehensive usage examples

## 🔄 Changelog

### v0.1.0

- Initial release
- Pydantic V2 configuration models
- Environment variable substitution
- Internal reference resolution
- OpenAPI and Azure AI Foundry tool support
- Comprehensive validation and error handling

---

Built with ❤️ for the AI development community
