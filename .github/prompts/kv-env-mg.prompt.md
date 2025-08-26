---
mode: agent
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTaskGetOutput', 'runTasks', 'runTests', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'Microsoft Docs', 'microsoft.docs.mcp']
---
## Azure Key Vault Environment Variable Script Generation Prompt

You are an expert DevOps automation assistant. Your task is to generate three Bash scripts for managing environment variables in Azure Key Vault and update the project README.md with clear usage instructions.

### Goal

Create scripts to:
- **set**: Upload environment variables from a `.env` file to Azure Key Vault, prefixing each key with an app name.
- **get**: Download environment variables from Azure Key Vault to a local env file, removing the app name prefix and converting dashes to underscores.
- **del**: Delete environment variables from Azure Key Vault based on keys in a `.env` file, matching secrets with the app name prefix and converting underscores to dashes.

### Requirements

- Each script must accept:
  - `app_name` (prefix for secrets)
  - `-f` (env file path, default: .env.local for set/del, `.env.azure` for get)
  - `-k` (Azure Key Vault name, default: `kv-cdp-env`)
- Use Azure CLI for all Key Vault operations.
- Handle comments and empty lines in env files.
- For set/del: convert underscores in keys to dashes for Key Vault secret names.
- For get: convert dashes in secret names to underscores for env file keys.
- Scripts must be named:
  - `set_env_in_kv.sh`
  - `get_env_from_kv.sh`
  - `del_env_from_kv.sh`
- Include usage instructions and error handling in each script.

### README.md Update Instructions

After generating the scripts, update the project’s README.md to include a section for each script with:
- Script name and purpose
- Usage example
- Parameter descriptions
- Notes on Azure CLI requirements and naming conventions

### Output Format

Return each script as a separate Bash code block, with a brief description above each. Then, provide the README.md update as a Markdown code block.
