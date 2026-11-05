# Artefact Gold từ hướng dẫn Fabric

Nguồn: [Gold_Warehouse_Huong_dan_chi_tiet (3).docx](<../docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx>).
Lệnh `python -X utf8 tools/extract_gold_guide.py` tách nguyên văn 9 khối SQL
trong `fabric/sql/gold/` và 10 code cell thành hai notebook trong
`fabric/notebooks/`. Script kiểm tra đủ marker A–J và cú pháp Python của từng
cell; **chưa kiểm tra cú pháp T-SQL trong Fabric hoặc chạy bất kỳ item cloud nào**.

## Thứ tự triển khai

1. Kiểm kê workspace, SQL endpoint Silver, 17 bảng INT và
   `stg_sales_territory`; dùng `sql/preflight_silver.sql` để đối chiếu
   cột/kiểu, số dòng và status đơn hàng với SQL đã tách.
2. Thay `[sliver]` trong `A_source_adapters.sql` bằng tên SQL database thật.
   Giá trị này là chỗ thay thế trong tài liệu, chưa được xác nhận từ workspace.
3. Chạy A → B → C → D → E → F → G → H trên Warehouse mới. Mỗi khối là một
   query hoàn chỉnh; giữ các dấu `GO` khi chạy trong SQL editor.
4. Xác nhận status bán hàng, tiền tệ/tỷ giá, ngày cuối đủ dữ liệu và thời điểm
   quan sát tồn kho. Chỉ sau khi đối chiếu mới điền reviewer/cờ trong J và chạy.
5. Chạy Gold lần đầu, đọc `ops.gold_run`, `ops.dq_result` và đối chiếu fact,
   mart, rpt. Sau đó mới cấu hình pipeline và các notebook theo hướng dẫn.

Hai notebook còn placeholder GUID/ngày. Cell đầu cần được đánh dấu là
**parameter cell** trong Fabric và gắn `lh_gold_ml` làm default Lakehouse.
Notebook train phải hoàn tất và tạo model version trước khi score. Không dùng
nhãn `OBSERVED` cho dự báo xây trên dữ liệu lịch sử được tái dựng.

Các file trong `fabric/sql/gold/` và `fabric/notebooks/` được sinh từ DOCX;
chạy lại script sẽ ghi đè chúng. Nếu cần sửa do schema hoặc Fabric runtime,
ghi lý do và lưu bản triển khai đã chỉnh riêng để có thể đối chiếu với nguồn.

## Bootstrap xác thực read-only

Tạo chứng chỉ service principal và chỉ xuất public certificate:

```powershell
.\tools\fabric\New-FabricServicePrincipalCertificate.ps1
```

Upload file `.cer` được in ra vào Entra app registration. Sau khi tenant
admin đã bật Fabric public APIs cho app hoặc security group và app đã được
thêm vào workspace, chạy kiểm kê item:

```powershell
.\tools\fabric\Get-FabricWorkspaceInventory.ps1 `
  -TenantId '<tenant-guid>' `
  -ApplicationId '<application-guid>' `
  -CertificateThumbprint '<thumbprint>' `
  -WorkspaceId 'd0eaee60-9f3e-47b2-8aee-bbd327ab2062'
```

Các giá trị placeholder chỉ được truyền qua tham số lúc chạy; không ghi
tenant ID, app ID, thumbprint hoặc token vào notebook và mã nguồn. Script
kiểm kê chỉ gọi List Items API và không thay đổi workspace.
