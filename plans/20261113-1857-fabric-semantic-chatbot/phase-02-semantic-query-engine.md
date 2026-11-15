# Phase 02 - Semantic catalog, guardrails và DAX compiler

## Overview

- Priority: P0. Status: pending. Estimate: 1 ngày.
- Mục tiêu: Gemini chỉ chọn khái niệm hợp lệ; deterministic code tạo DAX đọc-only, bounded và testable.
- Context: [repo context](research/repo-context.md), [Fabric limits](research/fabric-access-options.md).

## Files to create

| Absolute path | Nội dung |
| --- | --- |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\config\semantic_model.yaml` | Curated live catalog, synonyms, sensitivity và business rules |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\schemas.py` | Pydantic `QueryPlan`, filter/sort/action/result models |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\catalog.py` | Load/index/validate catalog |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\query_guard.py` | Allowlist, types, caps, ambiguity/sensitivity checks |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\dax_compiler.py` | Logical plan -> bounded DAX templates |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\result_normalizer.py` | REST rows -> typed dataframe + warnings |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\unit\test_catalog.py` | Catalog contract |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\unit\test_query_guard.py` | Reject cases |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\unit\test_dax_compiler.py` | Golden DAX |

## QueryPlan contract

```python
class QueryPlan(BaseModel):
    action: Literal["query", "clarify", "reject"]
    title: str
    measures: list[str]
    dimensions: list[str]
    filters: list[FilterSpec]
    sort: list[SortSpec]
    limit: int = Field(ge=1, le=200)
    clarification_question: str | None = None
```

`FilterSpec.operator` chỉ gồm `eq`, `in`, `between`, `gte`, `lte`; value phải đúng catalog data type. Max 3 measures, 2 dimensions, 6 filters, 200 rows.

## Catalog requirements

- Exact live table/column/measure names và data types.
- Display name, Vietnamese/English synonyms, description và format/unit.
- `groupable`, `filterable`, `sensitive`, `allowed_values` khi cardinality thấp.
- Measure business definition, required companion measures, freshness/warning rules.
- Relationships dùng để giải thích/validate, không để model tự tạo relationship.
- Seed từ tutorial nhưng từng entry giữ `verified: false` đến khi đối chiếu live.

## DAX subset

- `SUMMARIZECOLUMNS` cho aggregate/group/filter.
- `TOPN` + `ORDER BY` cho top/bottom.
- `ROW` cho KPI scalar.
- Date filtering chỉ qua approved Date fields; time intelligence dùng measure có sẵn trong model.
- Compiler luôn tạo đúng một `EVALUATE`, một result table và hard row limit.
- Không chấp nhận raw DAX, calculated measure, `DEFINE MEASURE`, INFO/DMV hoặc identifier ngoài catalog.

## Business rules to encode

1. Net Sales/Orders/Quantity dùng semantic measures, không rebuild từ columns.
2. Margin request tự thêm Cost Coverage hoặc cảnh báo nếu companion measure thiếu.
3. Stock query tự thêm observation time/age; reject stock-history inference.
4. Forecast bắt buộc type, cutoff/horizon; reconstructed không được gọi operational.
5. Missing FX/data-health warnings đi kèm KPI liên quan.
6. Customer detail/name/email/address bị cấm trong MVP; aggregate-only.

## Implementation steps

1. Export/copy exact model metadata từ PBIP/TMDL/UI; reconcile tutorial names.
2. Chạy catalog validator: unique aliases, resolvable refs, valid types/relationships.
3. Implement escape functions riêng cho string/date/number/list.
4. Validate plan before compile, then validate compiled DAX invariants again.
5. Normalize fully-qualified column names, nulls, body warnings and truncation flags.
6. Add golden tests for scalar, grouped trend, top category, date range and multiple filters.

## Acceptance

- [ ] Unknown/sensitive identifiers, raw DAX, invalid operators/types và caps đều bị reject.
- [ ] Same logical plan always produces same DAX.
- [ ] 10 known-answer queries match Power BI values/filter context.
- [ ] Empty/null/truncated responses render deterministically with warning.
- [ ] Catalog version/hash included in diagnostics.

## Risk

Main risk is catalog drift. Mitigate bằng startup smoke queries, catalog version field và a maintenance checklist whenever Semantic Model changes.

