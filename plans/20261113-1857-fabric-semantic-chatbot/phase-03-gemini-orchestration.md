# Phase 03 - Gemini orchestration

## Overview

- Priority: P0. Status: pending. Estimate: 0.5-1 ngày.
- Mục tiêu: two-pass pipeline có ranh giới rõ: plan -> execute -> summarize.
- Context: [Gemini/security research](research/gemini-streamlit-security.md), [query engine](phase-02-semantic-query-engine.md).

## Files to create

| Absolute path | Nội dung |
| --- | --- |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\prompts\planner.md` | NL + catalog subset -> `QueryPlan` |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\prompts\summarizer.md` | Result -> grounded Vietnamese answer |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\gemini_client.py` | Official SDK wrapper, structured output, retry/usage |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\agent_service.py` | Orchestrator/state machine |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\unit\test_agent_service.py` | Mocked branches |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\evals\questions.yaml` | Gold questions/plans/expected behavior |

## State machine

```text
RECEIVED -> PLANNED -> VALIDATED -> COMPILED -> EXECUTED -> SUMMARIZED
           | clarify/reject | validation error | API error | empty result
```

Every terminal state returns a typed response with request ID and safe user message.

## Planner

1. Send only current question, minimal prior context and relevant catalog slice.
2. Use Pydantic/JSON schema; action is query/clarify/reject.
3. Temperature 0-0.2; no tools; no credentials/model IDs.
4. Validate output in code. Allow one repair call only for malformed JSON/schema.
5. Business ambiguity (currency/date/forecast mode) must yield `clarify`, not guessed defaults.

## Summarizer

1. Receive normalized aggregate rows capped at 100, measure metadata, units, filters, freshness and warnings.
2. No tools/function calling; result cells are untrusted data, never instructions.
3. Must cite period/filters and distinguish observed fact vs inference.
4. Must not recalculate/alter returned numbers or claim cause.
5. For one scalar or deterministic error, allow code-generated response to skip second LLM call.

## History policy

- UI may show full session, but planner sees at most last 6 compact turns.
- Do not resend old result tables; store referenced filter/measure context only.
- Follow-up resolution may inherit explicit prior filters, but the new QueryPlan must restate them and pass validation.

## Reliability/cost

- Separate env model names; pin active stable versions in example config at implementation time.
- Timeout each LLM call; bounded exponential backoff for 429/5xx.
- Log usage/latency/status only; no raw prompt/result.
- Add simple per-session rate limit and one in-flight request lock.

## Acceptance

- [ ] 30-50 eval questions: valid plan rate, numeric accuracy, execution success, false refusal tracked.
- [ ] Ambiguous questions clarify; unsupported/write/PII questions reject.
- [ ] Prompt injection in user text or returned cells cannot bypass catalog/execute tools.
- [ ] Summaries preserve exact numbers/units/warnings from normalized result.
- [ ] Gemini outage returns a graceful message and never leaks internal prompt/secret.

## Privacy gate

Before live use, document whether Gemini project is unpaid or paid. Unpaid mode blocks sensitive fields and should only run the public/demo AdventureWorks scope.

