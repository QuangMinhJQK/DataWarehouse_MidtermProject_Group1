# Kế hoạch Data Agent ngoài Fabric bằng Streamlit + Gemini

Ngày: 13/11/2026. Trạng thái: **đề xuất, chưa triển khai code**. Target: `dataagent_fabric/`.

## Mục tiêu và phạm vi

- Thay phần UI/orchestration của Fabric Data Agent bằng chatbot Streamlit chạy ngoài Fabric.
- Giữ Fabric/Power BI Semantic Model làm nguồn chuẩn cho relationship, measure và KPI.
- Người dùng hỏi tiếng Việt/Anh; app trả lời, bảng dữ liệu và chi tiết truy vấn để đối soát.
- Chạy được sau khi điền Gemini key, Entra credential và semantic model ID.
- MVP chỉ đọc; không ghi Fabric, không chạy SQL tùy ý, không tạo purchase order/action.

## Kiến trúc chốt

```text
Streamlit -> Gemini structured QueryPlan -> allowlist/validator
          -> deterministic DAX compiler -> Power BI Execute Queries REST
          -> normalize/cap/redact -> Gemini summarizer -> answer + table + audit
```

Gemini không sinh DAX để chạy trực tiếp. Code chỉ chấp nhận logical plan tham chiếu catalog đã duyệt rồi tự tạo DAX giới hạn. Runtime access dùng `SemanticModelClient` interface; MVP là REST + service principal, đường nâng cấp là delegated REST hoặc Fabric IQ MCP.

## Quyết định chính

| Hạng mục | Chọn | Lý do |
| --- | --- | --- |
| Semantic access | Execute Queries REST | Nhẹ, Python thuần, không bắt buộc XMLA/capacity |
| Auth MVP | Service principal + client secret local | “Điền credential rồi chạy”; chỉ dùng model không RLS/SSO |
| LLM | `google-genai`, model qua env | SDK chính thức; đổi model không sửa code |
| Query generation | Structured plan + DAX compiler | An toàn, test được, không cho raw DAX |
| Schema | Curated YAML, verify với live model | REST không hỗ trợ DMV/INFO introspection |
| Framework | Streamlit monolith có module | KISS; chưa cần FastAPI, LangChain, vector DB |
| Data privacy | Aggregate-only; Gemini paid cho dữ liệu thật | Gemini unpaid không phù hợp dữ liệu nhạy cảm |

## Các phase

1. [Bootstrap, credentials và connectivity](phase-01-bootstrap-auth-connectivity.md) - 0.5 ngày.
2. [Semantic catalog, guardrails và DAX compiler](phase-02-semantic-query-engine.md) - 1 ngày.
3. [Gemini orchestration](phase-03-gemini-orchestration.md) - 0.5-1 ngày.
4. [Streamlit UX](phase-04-streamlit-ui.md) - 0.5 ngày.
5. [Tests, hardening, deployment và bằng chứng báo cáo](phase-05-testing-deployment.md) - 1 ngày.

## Gates trước khi chat được bật

- Semantic model đã tồn tại và `executeQueries` smoke test thành công.
- Tenant bật `Dataset Execute Queries REST API`; nếu dùng SP, bật service-principal API setting.
- SP có quyền cần thiết; model không có RLS/SSO. Nếu có, đổi sang delegated/Fabric IQ MCP.
- Catalog YAML khớp tên table/column/measure live; một known-answer query đối chiếu đúng Power BI.
- Không gửi PII/secrets/raw detail rows lên Gemini; unpaid Gemini chỉ dùng dữ liệu demo không nhạy cảm.

## Definition of done

- Fresh setup chạy bằng `uv sync` và `uv run streamlit run app.py` sau khi điền secrets.
- 10 câu hỏi nghiệp vụ lõi trả số đúng; câu mơ hồ hỏi lại; câu ngoài allowlist bị từ chối.
- UI hiện answer, table, logical plan/DAX, request ID và warning về freshness/truncation.
- Unit/integration/eval/adversarial tests đạt; không có secret trong Git/log/prompt.
- README ghi rõ giới hạn license, RLS, Gemini data terms và quy trình troubleshooting.

## Tài liệu nền

- [Bối cảnh repo và báo cáo](research/repo-context.md)
- [Nghiên cứu Fabric/Power BI access](research/fabric-access-options.md)
- [Nghiên cứu Gemini, Streamlit và bảo mật](research/gemini-streamlit-security.md)

## Câu hỏi còn mở

1. Tenant ID, external app client ID/secret và semantic model ID thật là gì?
2. Semantic model live có đúng `sm_gold_sales_inventory`, measure/table theo tutorial không?
3. Model có RLS/SSO không; app chỉ chạy local cho demo hay public/multi-user?
4. Gemini dùng unpaid quota với AdventureWorks demo hay paid tier?

