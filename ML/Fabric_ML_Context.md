# Fabric ML — AdventureWorks Sales

Tóm tắt để tiếp tục triển khai ba bài ML trong Microsoft Fabric. Ba loại bài toán đã chốt. Các notebook hiện dùng mô hình scikit-learn cố định; AutoML/FLAML chỉ được giữ lại như bối cảnh thử nghiệm cũ.

## 1. Wide table và mô hình

| Bài | Wide table trong `lh_gold_sales` | Grain | Target | Loại bài toán |
|---|---|---|---|---|
| A — Lượng bán 7 ngày tới | `dbo.ml_wide_demand_7d` | `product_key × as_of_date`, theo ngày | Tổng lượng bán từ t+1 đến t+7, kiểu số | Regression |
| B — Khách mua lại trong 30 ngày | `dbo.ml_wide_repeat_30d` | `customer_key × as_of_date`, mốc cách nhau 7 ngày | `1` nếu mua lại trong t+1 đến t+30, `0` nếu quan sát đủ 30 ngày mà không mua | Binary Classification |
| C — Nhóm sản phẩm mua tiếp trong 60 ngày | `dbo.ml_wide_next_category_60d` | `customer_key × as_of_date`, mốc cách nhau 7 ngày | Nhóm chính của giỏ ngày mua đầu tiên trong t+1 đến t+60. Nhãn là `BIKES`, `ACCESSORIES` hoặc `OTHER` | Multi-Class Classification |

| Bài | Nhóm mô hình đã bàn hoặc đề xuất | Baseline | Đánh giá trên holdout |
|---|---|---|---|
| A | Hồi quy cây tăng cường như XGBoost hoặc LightGBM. XGBoost là ứng viên đã bàn từ đầu. | Luôn dự báo 0. Lượng bán 7 ngày gần nhất (`qty_7`). | MAE chính, xem thêm MAE trên các dòng có bán. |
| B | Logistic Regression và cây tăng cường như LightGBM hoặc XGBoost. LightGBM là ứng viên đã bàn từ đầu. | Xác suất hằng bằng tỷ lệ mua lại trong train. | Average Precision và log loss, kèm tỷ lệ lớp dương. |
| C | Multinomial Logistic Regression và cây tăng cường đa lớp như CatBoost hoặc LightGBM. CatBoost là ứng viên đã bàn từ đầu. | Dự đoán lớp phổ biến nhất trong train. Dùng phân phối lớp train làm baseline xác suất khi tính log loss. | Macro F1, số mẫu từng lớp, có thể thêm log loss. |

Các notebook chốt **loại bài toán, cột dự đoán `target` và mô hình** trong code: `HistGradientBoostingRegressor` cho A và `LogisticRegression` cho B/C. Mô hình được fit trên `train_pool`, đánh giá trên holdout theo thời gian, log vào MLflow rồi đăng ký để batch scoring trong Fabric.

## 2. Dữ liệu và cách gán nhãn

### Nguồn từ Gold Warehouse

| Nguồn trong `wh_gold_sales` | Cột hoặc mục đích |
|---|---|
| `ops.publication` | `run_id`, `last_complete_date`. Chọn phiên có ngày hoàn chỉnh lớn nhất. SQL hiện dùng `run_id` để chọn nhất quán khi ngày trùng. |
| `mart.sales_line_approved` | `_gold_run_id`, `order_date_key`, `sales_order_id`, `customer_key`, `product_key`, `order_qty`, `net_line_amount`. Lọc theo đúng phiên Gold. |
| `dim.date` | `date_key`, `full_date`. Nối ngày bán và dựng lịch. |
| `dim.product` | `product_key`, `category_name`. Chuẩn hóa nhóm sản phẩm cho B/C. |
| `ml.product_eligibility_input` | `product_key`, `finished_goods_flag`, `active_start`, `active_end`. Xác định lịch bán hợp lệ cho A. |

### Features

| Bài | Cột | Cách tính |
|---|---|---|
| A | `qty_7`, `qty_14`, `qty_28` | Tổng số lượng trong 7/14/28 ngày đến hết ngày chốt t. |
| A | `std_28`, `positive_28`, `weekday` | Độ lệch chuẩn tổng thể của lượng bán ngày trong 28 ngày, số ngày bán dương trong 28 ngày, thứ của ngày chốt (Thứ Hai = 0). |
| B và C | `recency`, `buy_days`, `orders_90`, `units_90`, `net_90` | Số ngày từ lần mua gần nhất, số ngày có mua, số đơn phân biệt, tổng lượng bán và tổng tiền hàng ròng trong [t−89, t]. |
| B và C | `last_bikes`, `last_accessories`, `last_other` | Ba cột 0/1 thể hiện nhóm chính của giỏ ngày mua gần nhất. |

- **A.** Lấy thành phẩm trong thời gian đủ điều kiện bán, dựng đủ lịch ngày và điền 0 cho ngày không bán trong phạm vi có dữ liệu. Giữ giao dịch có `customer_key` trống. Cần 28 ngày lịch sử liên tục để tạo feature và đủ 7 ngày tương lai để gán nhãn. Bài toán dự báo **lượng bán quan sát được**.
- **B/C.** Giữ khách có giao dịch trong 90 ngày gần nhất. Gom đơn của cùng khách trong cùng ngày thành một giỏ. Nhóm chính có tổng lượng bán cao nhất, nếu hòa thì ưu tiên tên nhóm theo thứ tự chữ cái. Nhóm hợp lệ ngoài Bikes và Accessories gộp thành Other. Giỏ có nhóm nguồn thiếu được đánh dấu chưa xác định.
- **C.** Khi khách không mua trong 60 ngày hoặc giỏ ngày mua đầu tiên chưa xác định được nhóm, dòng không có nhãn huấn luyện. Kết quả C mô tả **nhóm hàng với điều kiện khách có mua lại** trong cửa sổ 60 ngày.

### Chia tập theo thời gian

- `coverage_start` là ngày có giao dịch đầu tiên của phiên Gold. `complete_end` lấy từ `last_complete_date`. `holdout_start = complete_end − 89 ngày`.
- `train_pool` có nhãn và cửa sổ nhãn kết thúc trước `holdout_start`. `holdout` có ngày chốt từ `holdout_start` và quan sát đủ cửa sổ nhãn. Các dòng train có cửa sổ nhãn chạm vùng holdout bị loại.
- `score` là dòng đủ điều kiện tại `complete_end`, với `target = NULL`. Giữ khóa, `as_of_date`, `data_split` và `source_gold_run_id` để đối soát. Mô hình chỉ nhận features và nhãn; các cột khóa không đưa vào huấn luyện.

## 3. Pipeline và notebook

- `wh_gold_sales` → ba **Copy data activities** → `lh_gold_sales` → notebook ML. Dán khối A/B/C tương ứng vào **Source → Query**. Mỗi khối tự tìm phiên Gold và tính mốc ngày. Giữ publication ổn định trong ba lần copy để cả ba đích cùng `source_gold_run_id`.
- Activity lần lượt là `Copy_Wide_Demand_7D`, `Copy_Wide_Repeat_30D`, `Copy_Wide_Next_Category_60D`. Dùng **Overwrite** cho toàn bộ snapshot. Kiểm tra schema mapping trước khi chạy vì chế độ này có thể thay schema đích.
- Notebook đọc trực tiếp `ml_wide_*`, lọc `train_pool` và `holdout` trước `toPandas()`, chỉ chọn feature cùng `target`.
- Thay `train_test_split` 80/20 bằng holdout đã chia trong wide table. Tách nhãn trước khi fit bộ tiền xử lý. Fit bộ điền thiếu trên train, áp dụng lại cho holdout. B/C cast `net_90` sang double trước khi đưa về pandas. C giữ nhãn dạng chuỗi.
- Không chạy CV/AutoML; holdout theo thời gian nằm ngoài quá trình fit và được dùng để báo cáo metric. Bộ điền thiếu chỉ fit trên `train_pool` rồi áp dụng lại cho holdout.

| Bài | Notebook | Experiment | ML Model item |
|---|---|---|---|
| A | `nb_automl_demand_7d` | `exp_automl_demand_7d` | `ml_model_demand_7d` |
| B | `nb_automl_repeat_purchase_30d` | `exp_automl_repeat_purchase_30d` | `ml_model_repeat_purchase_30d` |
| C | `nb_automl_next_category_60d` | `exp_automl_next_category_60d` | `ml_model_next_category_60d` |

## 4. Kết quả đã quan sát và phần còn mở

| Bài A | Số dòng | SKU | Target = 0 | Target > 0 | MAE luôn 0 | MAE dùng `qty_7` |
|---|---:|---:|---:|---:|---:|---:|
| Train pool | 124.909 | 295 | 58,66% | 51.642 dòng | 12,46 | 20,68 |
| Holdout | 16.351 | 197 | 57,09% | 7.017 dòng | **9,49** | 13,21 |

- Giữ bài A ở cấp SKU. Giữ các dòng target 0 khi train và khi chấm. So MAE mô hình với **9,49 trên đúng holdout này**.
- Kết quả AutoML cũ không còn là đường chạy chính. Khi triển khai lại, dùng metric holdout được log bởi mô hình cố định trong notebook thay vì chờ AutoML.ial song song qua Spark. Chưa có bằng chứng run hoàn tất, model được đăng ký hoặc metric holdout được tính. Xem Spark job progress. Nếu lần chạy phải khởi động lại, có thể dùng `force_cancel=True` cho Spark job vượt ngân sách tìm kiếm.
- B đã đối chiếu notebook sinh từ wizard và có hướng dẫn bỏ giới hạn. C đã có bản notebook sửa. Chưa có số dòng theo lớp hoặc kết quả holdout của B/C được xác nhận trong cuộc trao đổi.

## Tệp liên quan

- [Copy_Wide_Tables_Fabric.sql](https://chatgpt.com/library?file_id=libfile_add1edd5b93c8191af7ab5dee366ff52&account_id=personal)
- [Check_Demand_7D_Fabric.sql](https://chatgpt.com/library?file_id=libfile_bbd1939d8bb88191a26e0a3579a88fbe&account_id=personal)
- [nb_automl_next_category_60d.ipynb](https://chatgpt.com/library?file_id=libfile_d925c8f895648191909689e028b653db&account_id=personal)
