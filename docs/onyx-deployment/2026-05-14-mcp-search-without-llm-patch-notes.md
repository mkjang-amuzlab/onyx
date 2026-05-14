# MCP search without LLM patch notes

## Why this patch exists

This patch adds a CE-oriented MCP search tool that can return indexed sections without invoking an LLM. It was developed against a clean `v3.3.0` base and then layered with the custom MCP output policy work that already existed in the repo.

The main goals are:

- expose `search_indexed_documents_without_llm`
- keep the result shape section-based
- preserve redaction policy behavior
- make the patch easy to re-apply on a clean `v3.3.0` checkout

## What changed

### MCP server

- Added a CE direct-search helper:
  - `backend/onyx/mcp_server/search_backend_ce.py`
- Added the MCP tool wiring:
  - `backend/onyx/mcp_server/tools/search.py`
- Updated MCP auth and token helpers:
  - `backend/onyx/mcp_server/auth.py`
  - `backend/onyx/mcp_server/utils.py`
- Updated document set access helper for the MCP server:
  - `backend/onyx/mcp_server/resources/document_sets.py`
- Updated MCP server entrypoint:
  - `backend/onyx/mcp_server/api.py`

### Output policy

- Added tool-specific output shaping in:
  - `backend/onyx/mcp_server/output_policy.py`
- `search_indexed_documents_without_llm` now:
  - returns `raw` payloads only when raw output is explicitly allowed
  - otherwise redacts nested content while preserving `link` and `url`

### Tests

- Added unit tests:
  - `backend/tests/unit/onyx/mcp_server/test_search_without_llm.py`
  - `backend/tests/unit/onyx/mcp_server/test_output_policy.py`
  - `backend/tests/unit/onyx/mcp_server/test_search_tools_output_redaction.py`
- Added integration test:
  - `backend/tests/integration/tests/mcp/test_mcp_server_search_without_llm.py`
- Added unit test scaffolding:
  - `backend/tests/unit/onyx/mcp_server/conftest.py`

### Deployment docs

- Added a runbook for the output policy behavior:
  - `docs/onyx-deployment/2026-05-11-mcp-output-policy-runbook.md`
- Added this patch note to describe the custom MCP search patch and how to apply it.

## Patch application order

Use this sequence when re-basing the patch onto a clean `v3.3.0` tree:

1. Create a worktree from `v3.3.0`.
2. Apply the custom commits in order:
   - `9591a5d0b` `Add MCP output policy and 111 document set helper`
   - `b049a76d3` `Add MCP person-name redaction`
   - `aaf585719` `Strengthen MCP web search redaction`
   - `6ed56841f` `feat: add CE MCP search without llm`
   - `22f71add7` `fix: honor raw policy for ce direct search`
   - `8451a7f6e` `fix: redact search without llm output when raw is disabled`
3. Run `py_compile` on the touched MCP modules.
4. Rebuild the backend image.
5. Restart `api_server`, `background`, and `mcp_server`.
6. Validate the MCP tool with a real call.

## Verification commands

### Local syntax check

```powershell
python -m py_compile `
  backend/onyx/mcp_server/api.py `
  backend/onyx/mcp_server/auth.py `
  backend/onyx/mcp_server/output_policy.py `
  backend/onyx/mcp_server/resources/document_sets.py `
  backend/onyx/mcp_server/search_backend_ce.py `
  backend/onyx/mcp_server/tools/search.py `
  backend/onyx/mcp_server/utils.py
```

### MCP runtime check

```powershell
curl http://127.0.0.1:8090/health
```

Then call the new tool with a real query and confirm the response includes:

- `query`
- `total_results`
- `sections`
- `backend = ce_direct_search`
- `retrieval_mode = hybrid`
- `policy.mode`

### Example expected behavior

- When raw output is allowed, `policy.mode` should be `raw`.
- When raw output is disabled, nested text should be redacted.
- The result should remain section-based and should not require an LLM call.

## Known validation note

Local `pytest` in the ad-hoc Python environment may fail during collection with a `UnicodeEncodeError` in the import chain from `backend/onyx/connectors/models.py`. The failing collection path is not part of the MCP patch itself, but it is worth keeping in mind when reproducing tests outside the project runtime.

## Relevant files at a glance

- `backend/onyx/mcp_server/api.py`
- `backend/onyx/mcp_server/auth.py`
- `backend/onyx/mcp_server/output_policy.py`
- `backend/onyx/mcp_server/resources/document_sets.py`
- `backend/onyx/mcp_server/search_backend_ce.py`
- `backend/onyx/mcp_server/tools/search.py`
- `backend/onyx/mcp_server/utils.py`
- `backend/tests/integration/tests/mcp/test_mcp_server_search_without_llm.py`
- `backend/tests/unit/onyx/mcp_server/conftest.py`
- `backend/tests/unit/onyx/mcp_server/test_output_policy.py`
- `backend/tests/unit/onyx/mcp_server/test_search_tools_output_redaction.py`
- `backend/tests/unit/onyx/mcp_server/test_search_without_llm.py`

