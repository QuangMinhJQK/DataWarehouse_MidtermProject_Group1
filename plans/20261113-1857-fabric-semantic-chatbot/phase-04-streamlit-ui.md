# Phase 04 - Streamlit UX

## Overview

- Priority: P1. Status: pending. Estimate: 0.5 ngày.
- Mục tiêu: demo rõ luồng, trả lời dễ đọc, có audit details và lỗi actionable.

## Files to create/modify

| Absolute path | Action |
| --- | --- |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\app.py` | Implement page shell, chat loop, startup health gate |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\src\dataagent\ui.py` | Render message/result/error/details helpers |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\.streamlit\config.toml` | Non-secret theme/server defaults |
| `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric\tests\ui\test_app.py` | `streamlit.testing.v1.AppTest` smoke flows |

## Layout

- Header: “AdventureWorks Data Agent”, connection/catalog status and model freshness.
- Sidebar: example questions, Clear conversation, optional diagnostics, privacy/auth mode banner.
- Main: `st.chat_message`, `st.chat_input`, `st.status` stages.
- Assistant response: concise answer, `st.dataframe`, warnings, `st.expander` for logical plan/DAX/request ID.
- Never show access token/client secret/system prompt.

## Session model

```python
messages: list[{
  role, text, dataframe_records, query_plan, dax,
  request_id, warnings, error
}]
```

Initialize once per session; preserve across reruns; Clear deletes all values. Disable input while request is running to prevent duplicate calls.

## Error UX

- Config/auth/permission: show exact missing setting or admin checklist, no stack trace by default.
- Clarification: render a single concrete follow-up question.
- Empty result: state filters and suggest a narrower/alternative question.
- Rate limit/timeout: show retry timing; never loop indefinitely.
- Truncation/freshness: prominent warning adjacent to answer/table.

## Starter questions

1. “Doanh thu thuần và số đơn theo năm là bao nhiêu?”
2. “Top 5 danh mục theo doanh thu trong năm 2013.”
3. “Tỷ lệ giao trễ theo khu vực.”
4. “Sản phẩm nào cần đặt hàng lại, snapshot tồn kho lúc nào?”
5. “Dự báo historical demo 7 ngày tới khác lượng bán thực tế thế nào?”

Only include examples supported by verified catalog measures.

## Acceptance

- [ ] Fresh startup with valid secrets reaches Ready; invalid setup disables chat.
- [ ] Rerun preserves answer/table/DAX details without requery.
- [ ] Clear conversation removes session data.
- [ ] Mobile/narrow screen remains usable; chat containers not nested.
- [ ] AppTest covers happy path, clarification, permission error and empty result.

## Deployment boundary

Local/course demo can use shared SP. Any public URL must add authentication/access restriction before release because every visitor otherwise inherits the SP's data access.

