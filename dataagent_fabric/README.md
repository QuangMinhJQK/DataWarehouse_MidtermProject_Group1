# AdventureWorks Fabric Semantic Data Agent

Chatbot Streamlit chỉ đọc, dùng Gemini để tạo logical query plan và Power BI Execute DAX Queries REST API (Apache Arrow) để truy vấn Fabric Semantic Model `sm_gold_sales_inventory`.

## Kiến trúc

```text
Question
  -> Gemini structured QueryPlan
  -> catalog allow-list + type/cap guardrails
  -> deterministic DAX compiler
  -> Power BI Execute DAX Queries REST (Apache Arrow)
  -> normalize/cap results
  -> Gemini grounded summary
  -> Streamlit answer + table + DAX audit
```

Gemini không sinh raw DAX để chạy. Semantic Model vẫn là nguồn chuẩn của measure và relationship.

## Yêu cầu

- Python 3.12 và `uv`.
- Gemini API key.
- Microsoft Entra App Registration + client secret.
- Fabric tenant settings:
  - `Semantic Model Execute Queries REST API` enabled.
  - `Allow XMLA endpoints and Analyze in Excel with on-premises semantic models` enabled.
  - `Service principals can call Fabric public APIs` enabled for a dedicated security group.
- Service principal được thêm vào workspace chứa semantic model.
- Semantic model nằm trên Fabric/Premium capacity.
- Semantic model không dùng RLS/SSO khi chạy bằng service principal.

## Cấu hình

File `.env` đã được Git ignore. Có thể tạo lại từ template:

```powershell
Copy-Item .env.example .env
```

Các biến bắt buộc:

```env
GEMINI_API_KEY=
GEMINI_MODEL_PLANNER=gemini-3.5-flash
GEMINI_MODEL_SUMMARIZER=gemini-3.5-flash-lite
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
POWERBI_WORKSPACE_ID=d0eaee60-9f3e-47b2-8aee-bbd327ab2062
POWERBI_SEMANTIC_MODEL_ID=58ae8006-e9ca-4010-9ee1-6ad9a1d85c0a
```

Không gửi `.env`, token hoặc secret vào chat, issue, screenshot hay Git.

## Chạy

```powershell
uv sync
uv run python scripts/smoke_test.py
uv run streamlit run app.py
```

Mở URL Streamlit in ra terminal, mặc định thường là `http://localhost:8501`.

## Kiểm tra chất lượng

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pytest --cov=src/dataagent
```

## Semantic catalog

`config/semantic_model.yaml` được dựng từ live TMDL definition ngày 13/11/2026. Catalog chứa:

- Measure được phép dùng.
- Dimension/filter được phép dùng.
- Vietnamese/English synonyms.
- Data types và query caps.
- Companion measures và business warnings.

Khi Semantic Model thay đổi, cần cập nhật catalog và chạy lại known-answer tests trước khi bật chat.

## Guardrails

- Read-only; đúng một DAX query và một result table.
- Tối đa 3 measure do người dùng yêu cầu, 2 dimension, 6 filter và 200 result rows.
- Catalog bị khóa theo workspace/model ID; cấu hình trỏ nhầm model sẽ fail-closed.
- Không cho sort theo field nằm ngoài output; trend mặc định sắp theo dimension tăng dần.
- Chặn kết hợp nhiều dimension cardinality cao trước khi tạo DAX.
- Customer name, email, address và các detail identifier không được đưa vào catalog.
- Stock được mô tả là snapshot kèm observation time/age.
- Historical demo forecast không được mô tả là dự báo vận hành hiện tại.
- Result cells là untrusted data, không phải instruction cho Gemini.
- Không cache query results trên server trong MVP.

## Data privacy

Gemini unpaid quota chỉ phù hợp dữ liệu demo/không nhạy cảm. Google có thể dùng input/output unpaid để cải thiện sản phẩm và human reviewers có thể xử lý nội dung. Dữ liệu thật cần Gemini paid tier hoặc nền tảng có điều khoản doanh nghiệp phù hợp.

## Troubleshooting

| Lỗi | Kiểm tra |
| --- | --- |
| Entra authentication failed | Tenant ID, client ID, client secret value/expiry |
| Execute DAX Queries bị từ chối | Bật `Semantic Model Execute Queries REST API`, XMLA endpoint và kiểm tra Read/Build |
| HTTP 403 | Tenant settings, security-group membership, workspace access, Read/Build |
| Model not found | Workspace ID và semantic model ID |
| RLS/SSO model | Chuyển sang delegated user OAuth/Fabric IQ MCP; không dùng shared SP |
| Gemini model unavailable | Đổi model stable đang có trong Google AI Studio qua `.env` |
| Empty result | Filter values/date range và data freshness |

## Phạm vi triển khai

MVP này phù hợp local/course demo với shared service principal. Không public app ra Internet nếu chưa có authentication/access gate, vì mọi visitor sẽ dùng chung quyền của service principal.

