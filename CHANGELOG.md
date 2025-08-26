# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-26

### Changed
- **BREAKING**: Simplified import structure - can now import directly from `agents_config` instead of `app.agents_config`
- Updated `pyproject.toml` with proper package directory mapping
- Updated all documentation and examples to use new import structure

### Fixed
- Fixed GitHub Actions release workflow to use modern `softprops/action-gh-release` instead of deprecated `actions/create-release`
- Added proper permissions for GitHub release creation

### Migration Guide
**Before (v0.1.x):**
```python
from app.agents_config.config_loader import ConfigLoader
from app.agents_config.ai_config import AIConfig
```

**After (v0.2.0+):**
```python
from agents_config.config_loader import ConfigLoader
from agents_config.ai_config import AIConfig

# Or directly from main module:
from agents_config import ConfigLoader, AIConfig
```

## [0.1.1] - 2025-08-26

### Added
- Initial release of agents-config library
- Pydantic V2 validation for AI agent configurations
- Environment variable substitution with `${env:VAR_NAME}` syntax
- Internal reference resolution with `${ref:path.to.value}` syntax
- Support for Azure OpenAI, OpenAI, and Ollama model providers
- OpenAPI and Azure AI Foundry tool integrations
- Cross-reference validation between agents, models, and tools
- Comprehensive test suite and documentation

### Features
- **Configuration Loading**: Load from YAML files or Python dictionaries
- **Model Management**: Configure multiple AI models with different providers
- **Agent Configuration**: Define agents with specific models and tools
- **Tool Integration**: Support for external tools via OpenAPI or Azure AI Foundry
- **Validation**: Comprehensive validation with clear error messages
- **Environment Flexibility**: Support for different deployment environments

[Unreleased]: https://github.com/kdcllc/agents_config/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/kdcllc/agents_config/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/kdcllc/agents_config/releases/tag/v0.1.1