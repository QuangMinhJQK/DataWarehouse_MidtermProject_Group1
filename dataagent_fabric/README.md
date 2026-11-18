# AdventureWorks Fabric Semantic Data Agent

Ứng dụng Streamlit gồm dashboard Fabric công khai và chatbot chỉ đọc. Chatbot dùng Gemini để tạo logical query plan và Power BI Execute DAX Queries REST API (Apache Arrow) để truy vấn Fabric Semantic Model `sm_gold_sales_inventory`.

Trang **Dashboard** mở mặc định và nhúng report đã `Publish to web`. Trang **Data Agent** mở công khai theo yêu cầu demo; API key và client secret chỉ được đọc ở phía máy chủ. Link dashboard public cũng có thể được mở trực tiếp ngoài app.

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

## Triển khai Streamlit Community Cloud

1. Đẩy mã nguồn lên GitHub. Chọn entrypoint `dataagent_fabric/app.py` và Python 3.12. File `dataagent_fabric/requirements.txt` khai báo các thư viện để Cloud cài đặt.
2. Trong **Advanced settings → Secrets**, nhập các biến ở cấp cao nhất của TOML. Dùng **giá trị thật trong Secrets UI**, không điền vào file trong repo:

   ```toml
   GEMINI_API_KEY = "<api-key>"
   GEMINI_MODEL_PLANNER = "<model-name>"
   GEMINI_MODEL_SUMMARIZER = "<model-name>"
   FABRIC_AUTH_MODE = "service_principal"
   AZURE_TENANT_ID = "<tenant-uuid>"
   AZURE_CLIENT_ID = "<application-uuid>"
   AZURE_CLIENT_SECRET = "<client-secret-value>"
   POWERBI_WORKSPACE_ID = "<workspace-uuid>"
   POWERBI_SEMANTIC_MODEL_ID = "<model-uuid>"
   POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
   POWERBI_API_BASE_URL = "https://api.powerbi.com/v1.0/myorg"
   ```

3. Giữ file `.env` cục bộ và `.streamlit/secrets.toml` ngoài Git. Kiểm tra bằng `git status --short` trước khi push. Nếu đã từng commit secret, cần thu hồi và tạo secret mới; xóa khỏi commit hiện tại không xóa được lịch sử Git.
4. Cho service principal quyền tối thiểu trên đúng workspace/semantic model. Đặt hạn mức quota cho Gemini và giám sát Fabric API. Vì Data Agent không có đăng nhập, mọi người có URL đều có thể dùng chung quota và quyền đọc tổng hợp của service principal.

Code không trả giá trị credential, exception thô hoặc traceback lên giao diện. Chỉ lưu request ID và loại lỗi trong log. Không bật `LOG_LEVEL=DEBUG` khi triển khai công khai.

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

MVP này phù hợp local/course demo với shared service principal và dữ liệu không nhạy cảm. Bản triển khai công khai cho phép mọi visitor dùng chung quyền của service principal; nếu dữ liệu hoặc quota cần giới hạn theo người dùng, cần thêm xác thực thực sự và phân quyền riêng.

