# Bàn giao phiên: tự động hóa Fabric và báo cáo LaTeX

Ngày: 05/11/2026. Workspace: `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1`.

## Mục tiêu và quyền

- Người dùng làm đồ án kho dữ liệu theo hướng data platform end to end: Azure SQL Database → Microsoft Fabric (đã làm đến Silver theo lời người dùng) → Gold/Warehouse → pipeline/ML/semantic model/report → bằng chứng → báo cáo LaTeX 7 chương trong `docs/`.
- Người dùng cho phép agent tự thực thi, kiểm tra và tự động hóa các bước tiếp theo; khi viết văn báo cáo phải áp dụng skill `humanizer:humanizer` mà không làm thay đổi dữ kiện, số liệu hay trích dẫn.
- Người dùng xác nhận **có quyền quản trị Microsoft Entra/Fabric tenant** và đã mở Fabric trên Edge. Không gửi hoặc lưu mật khẩu, token, private key trong chat/repo.
- Workspace Fabric URL: `https://app.fabric.microsoft.com/groups/d0eaee60-9f3e-47b2-8aee-bbd327ab2062/list?experience=fabric-developer`; ID `d0eaee60-9f3e-47b2-8aee-bbd327ab2062`.

## Việc đã làm

- Plan chính: `plans/20261105-1334-fabric-report-automation/plan.md`; thông tin nguồn và hiện trạng: `plans/20261105-1334-fabric-report-automation/artifact.md`.
- Đã đọc `docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx`, trích SQL A–J và hai notebook bằng `tools/extract_gold_guide.py` vào `fabric/`; đã kiểm tra nội dung trích xuất khớp DOCX và Python cell đúng cú pháp. `fabric/sql/preflight_silver.sql` là truy vấn kiểm kê Silver. **Chưa chạy SQL hoặc notebook trên Fabric.**
- `docs/source/content/tableofcontent.md` có mục lục 7 chương; `docs/main.tex` vẫn là khung 5 chương. MiKTeX/latexmk/XeLaTeX đã hoạt động ở phiên trước.
- Silver có 17 bảng INT và `stg_sales_territory` **chỉ là giả định từ DOCX**; chưa kiểm kê live, chưa xác nhận schema/row count/role/capacity.
- Azure SQL theo ảnh cũ: DB `adventureworksnhom1`, server `adventureworksgroup1.database.windows.net`, resource group `datawarehouse`, Azure for Students, Japan East, Standard S0. Cần kiểm tra live.

## Vướng xác thực và hướng đã chọn

- `Connect-AzAccount` theo **device code** bị Entra từ chối `530035`; Microsoft giải thích security defaults chặn luồng này. Đã dừng, không thử lặp lại. Đăng nhập WAM tương tác không hiện cửa sổ ở desktop người dùng. Lệnh mở Edge riêng có remote debugging bị hệ thống phê duyệt tự động chặn. Edge hiện tại người dùng dùng được nhưng agent chưa điều khiển được phiên đó.
- Hướng tiếp theo: app registration + service principal dùng **certificate**. Cần tạo chứng chỉ RSA trong `Cert:\CurrentUser\My` (private key không xuất), xuất **public `.cer`** cho app registration. Trong Entra, thêm chứng chỉ vào app, tạo security group chứa service principal; trong Fabric Admin portal cho phép group ở setting **“Service principals can call Fabric public APIs”**; thêm app hoặc group vào workspace với quyền phù hợp, ban đầu tối thiểu đọc để kiểm kê rồi Contributor khi triển khai.
- Máy có `Az.Accounts` 5.5.4, `New-SelfSignedCertificate` và `Export-Certificate`. **Chưa tạo chứng chỉ; chưa tạo app registration, group, script xác thực hay thử API.** Agent trước bị ngắt đúng trước bước này.
- Tài liệu Microsoft đã kiểm tra live bằng `Invoke-WebRequest` vì công cụ `web__run` trả lỗi 404 trong phiên này:
  - [Fabric identity support](https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support)
  - [Fabric tenant developer settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-developer): setting public APIs cho phép service principal trong security group được chọn.
  - [List Items API](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items): `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items`, hỗ trợ service principal/managed identity.
  - [Azure PowerShell certificate login](https://learn.microsoft.com/en-us/powershell/azure/authenticate-noninteractive): `Connect-AzAccount -ServicePrincipal -ApplicationId ... -Tenant ... -CertificateThumbprint ...`.
  - [Error 530035](https://login.microsoftonline.com/error?code=530035), [security defaults](https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults).
- Fabric API và item support thay đổi theo item; riêng tạo Warehouse bằng service principal có tài liệu không hoàn toàn nhất quán. Kiểm tra API thực tế trước khi cam kết tự động hóa mọi item. Fabric Data Agent có điều kiện capacity paid F2+/P1+ theo kiểm tra trước, trial có thể không đủ.

## Bước tiếp theo rõ ràng

1. Tạo chứng chỉ non-exportable trong `Cert:\CurrentUser\My`, xuất public `.cer` vào nơi hợp lý và cập nhật `.gitignore` nếu tạo file chứa thông tin cục bộ; không xuất PFX/private key. Nên tạo script lặp lại được và ghi thumbprint để người dùng upload chứng chỉ. Kiểm tra tài liệu Microsoft về tham số chứng chỉ và khả năng `Connect-AzAccount` khi app chưa có Azure subscription.
2. Viết script PowerShell kiểm kê chỉ đọc qua Fabric API, nhận `TenantId`, `ApplicationId`, `CertificateThumbprint`, `WorkspaceId`; lấy token cho `https://api.fabric.microsoft.com`, gọi List Items, in tên/loại/ID item và lỗi hữu ích, không in token. Chỉ chạy sau khi người dùng hoàn tất app registration/tenant setting/workspace permission.
3. Cập nhật `plan.md` với lộ trình bootstrap và giới hạn browser; tạo hướng dẫn UI ngắn, cụ thể để người dùng làm các thao tác admin một lần. Có thể hỏi tenant ID và app ID **sau khi** chuẩn bị đầy đủ bước agent tự làm; không hỏi mật khẩu/token.
4. Khi API hoạt động, kiểm kê Silver **read-only** trước; xác nhận capacity, item, schema, row count, rồi mới triển khai Gold theo plan. Thu bằng chứng có nguồn gốc, không gọi `RECONSTRUCTED` prediction là dự báo vận hành hiện tại.
5. Viết báo cáo từ kết quả thật theo mục lục 7 chương, áp dụng skill `humanizer:humanizer`, build và kiểm tra PDF.

## Lưu ý repo

- `git status` trước lúc ngắt: `.gitignore` và `.vscode/settings.json` đã sửa từ phiên trước; `docs/`, `fabric/`, `plans/`, `tools/` chưa được Git theo dõi. Không xóa/ghi đè các thay đổi này.
- Không có `AGENTS.md`, `CLAUDE.md` hoặc `development-rules.md` được tìm thấy bằng `rg --files` tại repo và thư mục cha.
- Kỹ năng `planning` đã đọc trong phiên hiện tại; quy định của nó thiên về lập plan. `postman:api-engineer` đã đọc do nhiệm vụ tích hợp Fabric API; script kiểm kê chưa viết. Khi viết văn báo cáo, cần đọc `humanizer:humanizer` trước khi dùng.
