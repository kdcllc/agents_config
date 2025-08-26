---
mode: 'agent'
description: 'Create Azure DevOps Work Item of type **Issue** using the `wit_create_work_item` tool to implement the specification in the spec file [${input:SpecFile}](../spec/${input:SpecFile}).'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'ado', 'search_code', 'search_workitem', 'wit_add_child_work_item', 'wit_add_work_item_comment', 'wit_close_and_link_workitem_duplicates', 'wit_create_work_item', 'wit_get_query', 'wit_get_query_results_by_id', 'wit_get_work_item', 'wit_get_work_item_type', 'wit_get_work_items_batch_by_ids', 'wit_get_work_items_for_iteration', 'wit_link_work_item_to_pull_request', 'wit_list_backlog_work_items', 'wit_list_backlogs', 'wit_list_work_item_comments', 'wit_my_work_items', 'wit_update_work_item', 'wit_update_work_items_batch', 'wit_work_items_link']
---

Create an Azure DevOps Work Item of type **Issue** using the `wit_create_work_item` tool to implement the specification in the spec file [${input:SpecFile}](../spec/${input:SpecFile}).
If the work item already exists, update it with the latest information from the spec file.

Default ADO project name is `SB Corporate Data`.

Use the following template for the Issue:

---

name: "🚀 Feature request"
description: Suggest an idea or enhancement for the solution accelerator
title: "[Feature]: <short summary of the feature>"
labels: [enhancement]
fields:

- Area: Which part of the solution does this enhancement relate to? (Options: Infrastructure (Bicep/infra), Application Services (API, Functions, etc.), UI (Web app, Portal, etc.), Documentation, Other)
- Motivation: What problem does this feature solve? Why is it needed?
- Proposed Solution: Describe the solution you'd like.
- Alternatives Considered: Have you considered any alternative solutions or features?
- Additional Context: Add any other context or screenshots about the feature request here.

Populate each The single word "field" lacks sufficient context and detail to generate a meaningful enhanced prompt. Please provide:

1. The intended use or context for the field
2. Any specific requirements or constraints
3. The type of response you're seeking
4. The domain or subject area this relates to

For example:
- Is this about a database field?
- A form input field?
- A field in object-oriented programming?
- A scientific or mathematical field?

This will help create a precise, actionable prompt that meets your needs. using the information from the specification file. The Issue should be clear, concise, and structured to facilitate understanding and implementation by the development team. Only apply changes that are necessary to implement the specification file and not any other changes that are already implemented.
