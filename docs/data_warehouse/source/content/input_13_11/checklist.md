1. Phạm vi chính thức

- Rubric/mẫu trình bày của giảng viên.
- Hạn nộp, số trang mong muốn.
- Web Application và Data Agent là bắt buộc, đã làm, hay chỉ là hướng phát triển?
- Thông tin bìa: GVHD, thành viên, MSSV, lớp, thời gian và phân công.

2. Hiện trạng thật trên Fabric

- Danh sách item trong workspace: Lakehouse, Warehouse, Data Pipeline, Dataflow Gen2, Notebook, Semantic Model, Report, ML Model.
- Tên chính xác của từng item.
- Ảnh canvas pipeline và lịch sử chạy thành công.
- Connection type từ Azure SQL; chỉ cần tên server/database đã che thông tin nhạy cảm.
- Không cần gửi mật khẩu, token hoặc connection string chứa secret.

3. Bronze, Silver và Gold

- Danh sách bảng và số dòng từng tầng.
- STG đã chuẩn hóa những gì: tên cột, kiểu dữ liệu, null, trùng lặp…
- INT đã join bảng nào và áp dụng quy tắc nghiệp vụ nào.
- Danh sách bảng chiều, bảng fact và data mart tại Gold.
- Script Power Query/SQL/notebook hoặc ảnh các bước xử lý.
- Cơ chế full load hay incremental, lịch chạy và xử lý lỗi.

4. Quyết định nghiệp vụ cho Data Warehouse

- Grain chính xác của fact bán hàng.
- Trạng thái đơn hàng nào được tính doanh thu.
- Công thức doanh thu: LineTotal, OrderQty × UnitPrice × (1 − Discount) hay công thức khác.
- Chọn OrderDate, ShipDate hay DueDate làm ngày nghiệp vụ.
- Quy tắc tiền tệ, thuế, phí vận chuyển và đơn hủy/trả.
- Cách xác định Online/Reseller.
- Các dimension, surrogate key, unknown member và SCD type.
- DDL và script nạp Warehouse nếu đã có.

5. Semantic Model và Power BI

- Danh sách bảng được đưa vào model.
- Relationships, cardinality, filter direction và hierarchy.
- Danh sách measure DAX/KPI.
- Ảnh từng dashboard và câu hỏi nghiệp vụ mà dashboard trả lời.
- Số liệu đối chiếu giữa Power BI và SQL.

6. Machine Learning — cần chốt lại phạm vi

Hiện có một mâu thuẫn lớn:

- Mục lục yêu cầu dự báo doanh số và dự báo nhu cầu/nguy cơ hết hàng.
- Repo lại có ba bài: nhu cầu 7 ngày, mua lại trong 30 ngày, nhóm sản phẩm tiếp theo trong 60 ngày.
- Sơ đồ ghi Fabric AutoML, nhưng tài liệu ML hiện nói dùng mô hình scikit-learn cố định và không chạy AutoML.

Thông tin ba mô hình hiện tại nằm trong ML/Fabric_ML_Context.md

Nhóm cần xác nhận bộ bài toán nào là chính thức. Sau đó mình cần:

- Target, feature, grain và cửa sổ dự báo.
- Cách chia train/holdout.
- Baseline, thuật toán và tham số.
- Metric thực tế, confusion matrix/feature importance nếu có.
- Tên experiment/model trong Fabric, ảnh run thành công.
- Bảng lưu prediction và cách đưa kết quả vào báo cáo.

7. Kiểm thử và đánh giá

- Đối chiếu row count Source → Bronze → Silver → Gold.
- Kết quả kiểm tra null, duplicate, khóa ngoại và tổng doanh thu.
- Thời gian chạy pipeline và các lỗi từng gặp.
- Kết quả kiểm tra dashboard, ML và refresh.
- Hạn chế thực tế của trial/capacity/dữ liệu.