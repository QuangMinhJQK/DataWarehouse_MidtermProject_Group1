# Phase 01 - Bootstrap, credentials và connectivity

## Overview

- Priority: P0. Status: pending. Estimate: 0.5 ngày.
- Mục tiêu: fresh clone cài được; validate config; lấy token; chạy một known-good DAX query trước khi xây chatbot.
- Context: [Fabric access research](research/fabric-access-options.md), [repo context](research/repo-context.md).

## Files to create

| Absolute path | Nội dung |
| --- | --- |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\pyproject.toml` | Python 3.11+, runtime/dev dependencies, Ruff/Pytest config |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\app.py` | Streamlit entrypoint tối thiểu |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\.env.example` | Placeholder, không secret |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\.streamlit\secrets.example.toml` | Mapping secrets cho deploy |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\config.py` | Pydantic settings, fail-fast validation |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\auth.py` | MSAL confidential client/token acquisition |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\fabric_client.py` | `SemanticModelClient` + REST implementation |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\scripts\smoke_test.py` | Auth + single measure query diagnostic |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\README.md` | Setup, tenant settings, permissions, runbook |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\.gitignore` | Bổ sung local secrets/token/log patterns nếu thiếu |

Use package layout `src/dataagent/`; add `__init__.py`. Update root `.gitignore` only if it does not already exclude `.env`, `.streamlit/secrets.toml`, token cache and local logs; preserve existing user edits.

## Dependencies

Runtime: `streamlit`, `google-genai`, `pydantic`, `pydantic-settings`, `msal`, `httpx`, `pandas`, `tenacity`, `pyyaml`. Dev: `pytest`, `pytest-mock`, `respx`, `ruff`.

## Implementation steps

1. Create `uv` project; pin compatible major/minor ranges and lock file.
2. Define settings: Gemini key/models; auth mode; tenant/client/secret; workspace/model IDs; HTTP timeouts; row caps; log level.
3. Load priority: environment -> Streamlit secrets -> defaults. Never read real secret from committed YAML.
4. Validate UUIDs, required settings per auth mode and caps at startup; error names missing variable without echoing value.
5. Implement MSAL client-credential flow with Power BI `.default` scope; keep token in memory and refresh before expiry.
6. Implement REST call, correlation ID, timeout, response body/error parsing, 401/403/429/5xx classification.
7. Smoke query an allowlisted existing measure, e.g. `EVALUATE ROW("Value", [Net Sales])`; parameterize measure in case live name differs.
8. README tenant checklist: Execute Queries enabled; service principals enabled; SP granted workspace/model access; RLS/SSO restriction.

## Failure handling

- 401: tenant/client/secret/scope invalid.
- 403: tenant setting, workspace membership, Read/Build or license/capacity issue.
- 404: semantic model ID wrong or caller cannot see it.
- 429: honor `Retry-After`, bounded retry.
- 200 with body error/truncation: treat as failure/warning, not success.

## Todo / acceptance

- [ ] `uv sync` works on Windows PowerShell.
- [ ] Missing config fails before Streamlit opens chat.
- [ ] Smoke test prints only status, request ID, latency and aggregate value; never token.
- [ ] Wrong credentials and wrong model ID produce actionable messages.
- [ ] No code past this gate assumes semantic access works.

## Security

Client secret is acceptable only for local/course demo. A public deployment requires user auth/access gate and secret manager; if model has RLS/SSO, stop and redesign auth before phase 2.

