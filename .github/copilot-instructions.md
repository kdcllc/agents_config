## Project Context

This repository automates email workflows using Azure Logic Apps, Azure Container Apps, Azure OpenAI, and Azure Search. It is primarily a Python backend with FastAPI, modular agents, Jinja2 prompt templates, and Terraform-based infrastructure.

````instructions
# GitHub Copilot Custom Instructions for Cyclotron Agent Framework

## Project Overview

This repository implements a modular AI agent framework for orchestrating and running agents with configurable models and tools. It supports OpenAI, Azure OpenAI, Ollama, and custom tool integrations (OpenAPI, MCP). The system is designed for extensibility, secure configuration, and cloud-native deployment (FastAPI, Azure Functions).

## Architecture & Key Patterns

- **Definitions-Driven:** All agent, model, and tool configurations are stored in `/definitions/` (`agents/`, `models/`, `tools/`). Agents are defined by `definition.json`, `instructions.md`, and `dependencies.json`.
- **Central Loader:** `src/agent_loader.py` loads and wires agents, models, and tools, resolving environment variables and dependencies.
- **Extensible Tools:** Tools are defined as OpenAPI or MCP JSON specs in `/definitions/tools/`. The loader supports dynamic registration and configuration.
- **Model Registry:** Models are configured in `/definitions/models/model.json` and support environment variable substitution for secrets.
- **Agent Runner:** `src/agent_runner.py` provides CLI and async entrypoints for running agents, supporting streaming and chat history.
- **API & Orchestration:** FastAPI (`function_app.py`) and Azure Durable Functions (`durable_function.py`) expose agent execution as HTTP endpoints and orchestrations.

## Developer Workflows

- **Run Agent (CLI):**
  ```bash
  python -m src.agent_runner analyst "What's the weather in New York today?"
````

- **Run Agent (API):**
  - POST `/run_agent` with `agentName`, `prompt`, and optional model/parameters.
- **List Agents:**
  - GET `/list_agents` returns all available agents and their capabilities.

## Coding Conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) and project-specific Python guidelines in `.github/instructions/python.instructions.md`.
- Use type hints and PEP 257 docstrings for all functions/classes.
- Prefer modular, reusable code—see `src/agent_loader.py` and `src/models.py` for examples.
- Never hardcode secrets; use environment variables (see `${env:VAR}` in configs).
- Document edge cases and design decisions in comments.

## Project-Specific Patterns

- **Agent Definition Example:**
  ```json
  {
    "name": "Analyst",
    "description": "Data analysis agent",
    "model": "standard-assistant",
    "tools": ["weather", "stocks"]
  }
  ```
- **Tool Integration:** Use OpenAPI or MCP JSON specs. See `/definitions/tools/` for examples.
- **Prompt Engineering:** System instructions for agents are in `instructions.md` per agent.
- **Testing:** Place pytest-compatible tests in `/tests/`. Use fixtures and mock external dependencies.

## Integration Points

- **External APIs:** Tools integrate via OpenAPI or MCP protocols.
- **Cloud Deployment:** FastAPI for REST, Azure Functions for orchestration.
- **Secrets Management:** All API keys and secrets are injected via environment variables.

## References

- See `README.md` for architecture and usage.
- See `src/agent_loader.py` for agent/model/tool loading logic.
- See `/definitions/agents/` for agent configuration patterns.

## DevOps Guidance for Azure DevOps Pipeline Specification

- Ensure all pipeline YAML files are stored in the `az-devops/` directory.
- Use branch filters to trigger pipelines only on intended branches (`main`, `dev`, `develop`).
- Build and push Docker images to Azure Container Registry (`cdpregistrydev1`).
- Use Azure CLI tasks to update or restart Azure Container App (`ca-agents-cdp-dev` in `rg-cdp-dev`).
- Reference all secrets (ACR credentials, Azure credentials) from Azure DevOps variable groups; never hardcode secrets.
- PR pipeline should run tests if present, and skip gracefully if not.
- Document pipeline usage, triggers, and edge cases in the project README.
- Validate pipelines against specification criteria after implementation.
- Follow DORA metrics: deployment frequency, change failure rate, lead time for changes, and mean time to recovery.
- Automate all repeatable tasks and ensure traceability via Azure DevOps work items linked in the spec.
- All pipeline YAML files must use parameters for Azure Container Registry name, Azure Container App name, and resource group. This enables flexible deployment and easier configuration for different environments.

```

```
