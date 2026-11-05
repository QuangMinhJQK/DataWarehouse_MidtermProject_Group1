# Kế hoạch tự động hóa đồ án Azure/Fabric và báo cáo LaTeX

Ngày: 05/11/2026. Cập nhật sau khi đọc [hướng dẫn Gold/Warehouse](<../../docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx>). Trạng thái: **đã có hướng dẫn triển khai, chưa kiểm kê live workspace hoặc chạy Gold**. Người dùng đã cho phép thực thi và kiểm tra; các bước cloud bắt đầu sau khi có phiên truy cập phù hợp.

## 1. Những gì đã kiểm tra

| Hạng mục | Hiện trạng | Khả năng tiếp theo |
|---|---|---|
| Tutorial triển khai | DOCX Gold/Warehouse có SQL A–J, pipeline, ML, semantic model, report và Data Agent; [video YouTube](https://www.youtube.com/watch?v=4lyHIQl4VM8) chỉ hướng dẫn cài LaTeX | Dùng DOCX làm bản thiết kế để đối chiếu với tenant và kết quả chạy, không coi code trong DOCX là đã được nghiệm thu |
| Repo | `AdventureWorks/raw/` có CSV/SQL nguồn; `docs/source/content/` có mục lục 7 chương và nháp chương 1; `docs/main.tex` vẫn là khung 5 chương | Phân tích nguồn, chuyển đề cương 7 chương sang LaTeX, tạo bảng/sơ đồ từ kết quả thật |
| Build báo cáo | MiKTeX, Perl, `latexmk`, XeLaTeX hoạt động; PDF đã biên dịch | Có thể tạo chương, bảng, hình, tài liệu tham khảo và build tự động |
| Fabric/Azure | [artifact.md](artifact.md) ghi ảnh Azure SQL `adventureworksnhom1` và Fabric trial; đã có [URL workspace](https://app.fabric.microsoft.com/groups/d0eaee60-9f3e-47b2-8aee-bbd327ab2062/list?experience=fabric-developer), chưa kiểm tra được role hay item | Edge UI của người dùng mở được; Azure PowerShell device login bị security defaults chặn với mã 530035. Silver hoàn thành hiện là **giả định của kế hoạch** |
| Chụp màn hình | Có Microsoft Edge, Node và bộ script Puppeteer; chưa kiểm tra phiên Fabric đã đăng nhập | Có thể tự chụp UI khi truy cập được, kiểm tra ảnh và gắn vào báo cáo |
| Mục lục chi tiết | Đã có tại `docs/source/content/tableofcontent.md`; chưa thấy rubric/thang điểm riêng | Dùng mục lục để bám nội dung và kiểm tra rubric nếu có |
| Artefact cục bộ | Đã tách SQL A–J và notebook train/score vào [`fabric/`](../../fabric/README.md); Python cell qua kiểm tra cú pháp | Còn kiểm tra schema Silver và chạy thử T-SQL trên Fabric |

## 2. Cách làm đề xuất

**Nguồn sự thật:** tài nguyên đang chạy trên Azure/Fabric, mã cấu hình trong Git, kết quả kiểm tra và ảnh chụp có nguồn gốc rõ ràng. DOCX là hướng dẫn thao tác và chứa giả định nghiệp vụ; mỗi bước phải đối chiếu với Silver thực tế và [tài liệu Fabric hiện hành](https://learn.microsoft.com/en-us/rest/api/fabric/articles/).

1. **Đối chiếu hướng dẫn và đề cương.** Lập bảng `bước DOCX → item/SQL/notebook → checkpoint → ảnh/log → mục báo cáo`. Chốt ngay khác biệt phạm vi giữa tutorial Gold và mục lục 7 chương.
2. **Kiểm kê read-only.** Xác nhận workspace/capacity/role, tên SQL endpoint Silver, Dataflow STG/INT và 17 bảng `int_*` cùng `stg_sales_territory`; đọc schema, row count, ngày dữ liệu và lịch sử chạy. Dùng [List Workspaces API](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspaces) nếu có xác thực; kiểm tra UI khi cần. Không đưa mật khẩu/token vào Git hoặc ảnh.
3. **Chốt chính sách nghiệp vụ.** Đối chiếu bốn tham số mà DOCX yêu cầu: status nào tính bán hàng, đơn vị tiền và hướng tỷ giá, ngày nghiệp vụ cuối đủ dữ liệu, thời điểm quan sát tồn kho. Kiểm tra tolerance tiền, kỳ quota và coverage ML từ nguồn. Ghi quyết định và truy vấn chứng minh trước khi duyệt policy Gold.
4. **Triển khai Gold theo thứ tự.** Tách SQL A–J từ DOCX thành tệp có version, kiểm tra schema/cú pháp/giả định rồi chạy trên Warehouse mới `wh_gold_sales_fabric`. A tạo adapter; B tạo bảng; C tạo policy draft; D/E/F tạo manifest, view và bảng report; G/H tạo procedure; J duyệt policy sau kiểm tra. Chạy Gold lần đầu bằng GUID mới, đọc `ops.gold_run`, `ops.dq_result` và đối chiếu fact, mart, rpt. Không thay đổi Silver đã hoàn thành khi kiểm kê không yêu cầu.
5. **Điều phối và ML.** Tạo `pl_gold_end_to_end`; nối STG → INT → refresh Silver SQL endpoint → register Silver → load Gold, sau đó Copy dữ liệu sang `lh_gold_ml`, chạy notebook train/score, Copy prediction về Warehouse và publish. Kiểm tra từng checkpoint trước khi bật lịch. Prediction từ dữ liệu lịch sử phải ghi nhãn `RECONSTRUCTED`/Historical Demo như DOCX; không trình bày là dự báo nhu cầu vận hành hiện tại.
6. **Khai thác.** Tạo semantic model từ bảng vật lý `rpt`, kiểm tra relationship và storage mode, measure, report và đối chiếu với SQL. Fabric Data Agent là nhánh có điều kiện theo capacity/tenant settings; web application có trong mục lục nhưng không nằm trong DOCX này, nên cần thiết kế riêng hoặc điều chỉnh phạm vi báo cáo.
7. **Lưu artefact lặp lại được.** Lưu SQL, notebook, pipeline definition và cấu hình trong Git. Dùng [Fabric REST APIs](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item), [Notebook APIs](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-public-api) hoặc [Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration) ở nơi hỗ trợ item; dùng UI cho các bước cần giao diện. Không tạo trùng tài nguyên khi chạy lại.
8. **Kiểm chứng và bằng chứng.** Lưu run ID, thời gian, row count, null/duplicate/key checks, đối chiếu nguồn–đích và SQL–report. Chụp UI của item, pipeline, run, schema, semantic model và report; lưu metadata URL/item/thời điểm, kiểm tra ảnh, che email/ID cá nhân khi xuất bản. Sơ đồ kiến trúc vẽ từ cấu hình đã xác nhận.
9. **Viết báo cáo.** Chuyển mục lục 7 chương sang LaTeX; viết từ cấu hình, số liệu và bằng chứng thật; chèn bảng/hình/citation. Sau bản nháp từng chương, áp dụng `humanizer:humanizer`, giữ nguyên dữ kiện, số liệu, thuật ngữ và mã. Build XeLaTeX; rà lỗi font, bảng, hình, mục lục và tham chiếu.

## 3. Ranh giới tự động hóa

- **Làm được ngay tại máy:** phân tích CSV/SQL, lập bản đồ dữ liệu, chuẩn bị mã và cấu trúc báo cáo, biên dịch PDF.
- **Làm được sau khi có quyền truy cập:** kiểm kê và cấu hình Fabric/Azure, chạy pipeline, lấy kết quả thật, chụp UI. Fabric có [connector Azure SQL Database](https://learn.microsoft.com/en-us/fabric/data-factory/connector-azure-sql-database-overview), nhưng cần xác định chính xác database và cách kết nối trước khi chọn hoạt động cụ thể.
- **Không thể suy ra đáng tin cậy từ video:** trạng thái workspace của bạn, thông số kết nối, quyền/capacity, dữ liệu đã nạp, kết quả chạy. Các phần này phải được kiểm tra trực tiếp.
- **Ưu tiên kỹ thuật:** API hoặc artifact trong Git cho cấu hình lặp lại được; browser automation cho bước UI và ảnh; LaTeX cho bản cuối. Chi phí Fabric/Azure và quyền tạo tài nguyên cần được kiểm tra trước khi chạy khối lượng lớn.

## 4. Đầu vào cần bổ sung

**Để bắt đầu phiên triển khai, tối thiểu cần:**

1. **Đường kiểm kê live được tenant và môi trường cho phép.** Workspace URL đã có. Edge của bạn đang mở nhưng không bật cổng điều khiển; lệnh mở Edge riêng có remote debugging bị hệ thống phê duyệt tự động chặn (“blocked by policy”). Thử đăng nhập bằng Microsoft Azure PowerShell qua device code cũng bị Microsoft Entra từ chối với [mã 530035](https://login.microsoftonline.com/error?code=530035): security defaults chặn ứng dụng này. Không thử ứng dụng đăng nhập khác để lách chính sách. Trước mắt có thể dùng `fabric/sql/preflight_silver.sql` trong Fabric UI và cung cấp kết quả, hoặc nhờ quản trị viên xác định phương thức truy cập API được phép. Không gửi mật khẩu/token vào chat hoặc repo.
2. Xác nhận Silver đang chứa **17 bảng INT và `stg_sales_territory`** theo DOCX, hoặc cho biết khác biệt. Có thể thay xác nhận này bằng quyền kiểm kê read-only trong workspace.
3. Người chịu trách nhiệm xác nhận bốn định nghĩa nghiệp vụ ở bước 3. Tôi sẽ đề xuất giá trị dựa trên dữ liệu và truy vấn; cần bạn trả lời khi nguồn không thể tự quyết định ý nghĩa nghiệp vụ.

**Bổ sung khi có:** tài liệu `INT_Huong_dan_chi_tiet_cap_nhat(1).docx` mà hướng dẫn Gold dẫn chiếu; rubric của môn; giới hạn credit Azure/Fabric hoặc thời gian chạy; yêu cầu web app và Fabric Data Agent có bắt buộc hay không. Thiếu các tài liệu này không chặn bước kiểm kê ban đầu.

## 5. Mốc hoàn thành

- **M1:** kiểm kê live Silver/workspace, mapping DOCX–mục lục–bằng chứng, chính sách nghiệp vụ được ghi rõ.
- **M2:** Gold Warehouse và pipeline chạy lại được, DQ/đối chiếu nguồn–đích đạt yêu cầu.
- **M3:** ML demo, semantic model/report; Data Agent và web app theo khả năng tenant và phạm vi đã chốt.
- **M4:** bộ ảnh/log/bảng kết quả có nguồn gốc; báo cáo LaTeX 7 chương đã biên tập bằng `humanizer:humanizer`, PDF build thành công và khớp kết quả thật.
