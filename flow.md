# AdventureWorks on Microsoft Fabric

Brief cho Codex dựng sơ đồ kiến trúc Medallion. Dùng tiếng Anh cho toàn bộ nhãn hiển thị.

## Nguồn tham chiếu

- **Ảnh Fabric bên trái** là nguồn chính cho bố cục, thành phần và mũi tên. Bản nháp đang ghi “Bronze” trên cả ba cột. Đổi nhãn thành **Bronze**, **Silver**, **Gold** theo thứ tự từ trái sang phải.
- **Ảnh bên phải** cung cấp danh sách năm nhóm dữ liệu ở tầng nguồn. Phạm vi tham chiếu của ảnh này dừng ở khối Azure SQL Database.

## Khối và vị trí

| Vị trí | Nhãn hiển thị | Nội dung bên trong |
| --- | --- | --- |
| Bên trái, ngoài workspace | **Azure SQL Database** · **AdventureWorks** | Một database với năm nhóm schema xếp dọc theo thứ tự **Human Resources** (`HumanResources`), **Person** (`Person`), **Production** (`Production`), **Purchasing** (`Purchasing`), **Sales** (`Sales`). Dùng một icon Azure SQL cho khối nguồn và một đường ingest chung. |
| Cột 1 trong workspace | **Bronze** | **Lakehouse** · **Raw Source Tables**. |
| Cột 2 trong workspace | **Silver** | Một **Lakehouse** chứa hai khối nối tiếp từ trên xuống dưới. **STG — Data Standardization** chuẩn hóa tên cột, kiểu dữ liệu và kiểm tra chất lượng. **INT — Data Integration & Business Rules** ghép bảng và áp dụng quy tắc nghiệp vụ. |
| Cột 3, nửa trên | **Gold** → **Warehouse** | **Dimensions · Facts · Data Marts**. |
| Cột 3, nửa dưới | **Gold** → **Lakehouse** | **ML Features · Targets**. Ví dụ `ml_wide_repeat_30d` nếu sơ đồ cần tên bảng minh họa. |
| Bên dưới Gold | **Fabric AutoML / ML Model** | Nhánh huấn luyện từ Gold Lakehouse. Giữ vị trí bên dưới như ảnh Fabric. |
| Bên phải workspace | **Power BI**, **Data Agent** | Hai đích tiêu thụ, Power BI ở trên và Data Agent ở dưới. Giữ một điểm rẽ chung ở giữa như bản nháp. |

## Mũi tên

| Từ | Đến | Nhãn và cách vẽ |
| --- | --- | --- |
| Azure SQL Database | Bronze Lakehouse | **Data Pipeline · Copy Data**, nét liền. |
| Bronze Lakehouse | Silver STG | **Dataflow Gen2**, nét liền. |
| Silver STG | Silver INT | **Dataflow Gen2**, nét liền bên trong cùng một Lakehouse. Có thể dùng chung nhãn Dataflow Gen2 để tránh lặp. |
| Silver INT | Gold Warehouse | **Build Gold Tables**, nét liền. Nhãn mô tả chức năng vì ảnh chưa ghi tên activity. |
| Gold Warehouse | Gold Lakehouse | **Prepare ML Features & Targets**, nét đứt hướng xuống theo ảnh Fabric. |
| Gold Lakehouse | Fabric AutoML / ML Model | **Training Data**, nét liền hướng xuống. |
| Fabric AutoML / ML Model | Gold Lakehouse | Nét đứt hướng lên như bản nháp, thể hiện luồng trả kết quả ML. Giữ ở mức kiến trúc, với bảng đích và cách ghi chưa chốt trong brief. |
| Cạnh phải của cột Gold | Điểm rẽ → Power BI và Data Agent | Hai nhánh **Consumption**, nét liền. Bản nháp nối từ cột Gold nên dùng điểm rẽ chung. Icon tím ở điểm rẽ chưa có tên xác nhận, có thể biểu diễn bằng một nút nối trung tính. |

## Quy cách dựng hình

- Bố cục ngang, từ Azure SQL Database qua **Microsoft Fabric Workspace** đến hai đích tiêu thụ. Khung workspace bao ba cột Bronze, Silver, Gold. Trong Gold, Warehouse nằm trên Lakehouse.
- Dùng màu đồng, bạc và vàng cho ba cột. Dùng icon chính thức từ bộ icon Azure và Microsoft Fabric cho các dịch vụ đã xác định. Dùng đúng icon riêng cho **Lakehouse** và **Warehouse**, cùng icon Power BI và Data Agent ở nhánh tiêu thụ.
- Giữ tên dịch vụ, nhãn lớp và hướng mũi tên đọc được ở kích thước trình chiếu. Đặt nhãn transform trên hoặc cạnh đường nối. Dùng đường nối vuông góc để tránh cắt qua nhãn và khối.
