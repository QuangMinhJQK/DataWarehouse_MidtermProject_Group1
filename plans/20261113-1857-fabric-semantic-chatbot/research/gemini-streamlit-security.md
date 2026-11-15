# Nghiên cứu Gemini, Streamlit và bảo mật

## SDK và model policy

- Dùng `google-genai`; không dùng package legacy `google-generativeai`.
- Planner dùng JSON Schema/Pydantic structured output, gọi stateless và validate lại trong app.
- `GEMINI_MODEL_PLANNER` và `GEMINI_MODEL_SUMMARIZER` luôn đọc từ config.
- Khi implement, pin model stable đang hoạt động; không dùng alias `latest`.
- Planner temperature 0-0.2; timeout; exponential backoff cho 429/5xx; không retry mù 400.
- Function calling không cần cho MVP: explicit orchestration dễ kiểm soát và audit hơn autonomous loop.

## Data terms gate

Gemini unpaid Services có thể dùng input/output để cải thiện sản phẩm và human reviewers có thể xử lý nội dung. Google yêu cầu không gửi sensitive, confidential hoặc personal information vào unpaid Services.

Quyết định:

- Unpaid chỉ dùng AdventureWorks demo, aggregate-only, không gửi email/name/address/detail rows.
- Dữ liệu thật: dùng paid tier hoặc nền tảng có điều khoản doanh nghiệp phù hợp.
- Không gửi secrets, access token, prompt internals hoặc full chat history.

## Prompt-injection boundary

- User question, catalog text và result values đều là untrusted data.
- Planner không có tool và không tạo raw DAX; output phải qua Pydantic + allowlist + type checks.
- Summarizer không có tool, không thấy credentials/DAX compiler internals và được dặn coi result cells là data.
- Filter literals được escape theo type; reject unknown identifiers/operators, detail PII và limit vượt cap.
- Chỉ một repair attempt cho invalid structured output; sau đó trả lỗi rõ ràng.

## Streamlit state/caching

- `st.session_state.messages` lưu message riêng theo session.
- Assistant message giữ `text`, `rows`, `dax`, `query_plan`, `request_id`, `warnings`, `error`.
- `st.cache_resource` chỉ cho immutable catalog/client thread-safe.
- Không `st.cache_data` cho query results trong MVP vì cache server có thể chia sẻ giữa users.
- Clear button xóa history/results khỏi session.

## Logging/telemetry

Cho phép: timestamp, request ID, model name, plan status, DAX hash, duration, row count, HTTP status, token usage/cost estimate.

Cấm: secret/token, raw prompts, raw result rows, email/name/address, full DAX chứa sensitive filter literals.

## Nguồn

- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/)
- [Gemini API terms](https://ai.google.dev/gemini-api/terms)
- [Gemini billing/data privacy](https://ai.google.dev/gemini-api/docs/billing)
- [Streamlit chat input](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input)
- [Streamlit chat message](https://docs.streamlit.io/develop/api-reference/chat/st.chat_message)
- [Streamlit Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)

