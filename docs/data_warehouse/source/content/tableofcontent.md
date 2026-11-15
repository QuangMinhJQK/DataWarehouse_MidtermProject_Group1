**XÂY DỰNG GIẢI PHÁP KHO DỮ LIỆU TRÊN NỀN TẢNG MICROSOFT FABRIC CHO HOẠT ĐỘNG BÁN HÀNG CỦA ADVENTURE WORKS CYCLES**

**LỜI MỞ ĐẦU**  
**LỜI CẢM ƠN**  
**LỜI CAM KẾT**  
**MỤC LỤC**  
**DANH MỤC HÌNH ẢNH**  
**DANH MỤC BẢNG BIỂU**  
**DANH MỤC TỪ VIẾT TẮT**

# **CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN**

### **1.1. Bối cảnh thực tế**

### **1.2. Lý do chọn đề tài**

### **1.3. Mục tiêu dự án**

#### 1.3.1. Mục tiêu tổng quát

#### 1.3.2. Mục tiêu cụ thể

### **1.4. Đối tượng và phạm vi dự án**

#### 1.4.1. Đối tượng nghiên cứu

#### 1.4.2. Phạm vi nghiệp vụ bán hàng

#### 1.4.3. Phạm vi dữ liệu

#### 1.4.4. Phạm vi triển khai

### **1.5. Công nghệ và nền tảng sử dụng**

#### 1.5.1. Azure SQL Database

#### 1.5.2. Microsoft Fabric và OneLake

#### 1.5.3. Lakehouse và Medallion Architecture

#### 1.5.4. Fabric Data Factory

#### 1.5.5. Fabric Data Warehouse và Semantic Model

#### 1.5.6. Fabric Data Science và Machine Learning

#### 1.5.7. Power BI và Data Agent

### 

# **CHƯƠNG 2: MÔ TẢ VÀ PHÂN TÍCH DỮ LIỆU BÁN HÀNG**

### **2.1. Tổng quan về Adventure Works Cycles**

### **2.2. Tổng quan hoạt động bán hàng**

#### 2.2.1. Quy trình bán hàng

#### 2.2.2. Các đối tượng tham gia hoạt động bán hàng

#### 2.2.3. Các chỉ tiêu đánh giá hoạt động bán hàng

### **2.3. Nguồn gốc và cấu trúc dữ liệu**

#### 2.3.1. Nguồn dữ liệu Adventure Works

#### 2.3.2. Cấu trúc dữ liệu nguồn

#### 2.3.3. Các bảng dữ liệu phục vụ hoạt động bán hàng

#### 2.3.4. Mối quan hệ giữa các bảng dữ liệu

### **2.4. Khám phá và trực quan hóa dữ liệu**

#### 2.4.1. Phạm vi dữ liệu và phương pháp khám phá

#### 2.4.2. Kiểm tra chất lượng và khả năng liên kết

#### 2.4.3. Phân tích doanh thu theo thời gian

#### 2.4.4. Phân tích kênh bán hàng và khách hàng

#### 2.4.5. Phân tích cơ cấu sản phẩm

#### 2.4.6. Phân tích doanh thu theo lãnh thổ

#### 2.4.7. Kết luận từ khám phá dữ liệu

### **2.5. Xác định yêu cầu dữ liệu cho giải pháp**

#### 2.5.1. Xác định quy trình nghiệp vụ

#### 2.5.2. Xác định mức độ chi tiết dữ liệu

#### 2.5.3. Xác định các chiều phân tích

#### 2.5.4. Xác định các chỉ tiêu đo lường

#### 2.5.5. Xác định yêu cầu dữ liệu cho Machine Learning

# **CHƯƠNG 3: XÂY DỰNG KHO DỮ LIỆU TRÊN MICROSOFT FABRIC**

### **3.1. Kiến trúc tổng thể của giải pháp**

#### 3.1.1. Kiến trúc Microsoft Fabric

#### 3.1.2. Luồng dữ liệu trong hệ thống

#### 3.1.3. Vai trò của OneLake

#### 3.1.4. Vai trò của Lakehouse và Data Warehouse

### **3.2. Tích hợp dữ liệu với Microsoft Fabric**

#### 3.2.1. Kết nối và thu thập dữ liệu nguồn

#### 3.2.2. Xây dựng Data Pipeline

#### 3.2.3. Xây dựng Dataflow Gen2

#### 3.2.4. Phạm vi điều phối các quy trình tích hợp dữ liệu

### **3.3. Xây dựng Lakehouse theo Medallion Architecture**

#### 3.3.1. Tầng Bronze – dữ liệu nguồn

#### 3.3.2. Tầng Silver – dữ liệu làm sạch và chuyển đổi

#### 3.3.3. Tầng Gold – dữ liệu được chuẩn hóa phục vụ phân tích

#### 3.3.4. Luồng chuyển đổi dữ liệu giữa các tầng

### **3.4. Thiết kế Data Warehouse cho hoạt động bán hàng**

#### 3.4.1. Xác định Business Process và Grain

#### 3.4.2. Xây dựng Bus Matrix

#### 3.4.3. Thiết kế Dimension Tables

#### 3.4.4. Thiết kế Fact Tables

#### 3.4.5. Xây dựng mô hình Star Schema

### **3.5. Xây dựng Fabric Data Warehouse**

#### 3.5.1. Tạo và cấu hình Data Warehouse

#### 3.5.2. Xây dựng các bảng Dimension

#### 3.5.3. Xây dựng các bảng Fact

#### 3.5.4. Thiết lập khóa và mối quan hệ

#### 3.5.5. Nạp và đồng bộ dữ liệu

### **3.6. Xây dựng Semantic Model**

#### 3.6.1. Thiết kế mô hình dữ liệu phân tích

#### 3.6.2. Xây dựng Measures và KPI

#### 3.6.3. Thiết lập Relationships

#### 3.6.4. Kết nối với Power BI

# **CHƯƠNG 4: XÂY DỰNG CÁC MÔ HÌNH HỌC MÁY CHO HOẠT ĐỘNG BÁN HÀNG**

### **4.1. Chuẩn bị dữ liệu cho Machine Learning**

#### 4.1.1. Xác định phạm vi bài toán

#### 4.1.2. Xây dựng các tập dữ liệu dạng rộng

#### 4.1.3. Chia dữ liệu theo thời gian và tiền xử lý

### **4.2. Dự báo lượng bán trong 7 ngày tiếp theo**

#### 4.2.1. Biến mục tiêu và đặc trưng đầu vào

#### 4.2.2. Huấn luyện mô hình

#### 4.2.3. Baseline và tiêu chí đánh giá

### **4.3. Dự đoán khả năng mua lại trong 30 ngày**

#### **4.3.1. Xác định target và tập đặc trưng**

#### **4.3.2. Huấn luyện và đánh giá**

### **4.4. Dự đoán nhóm sản phẩm tiếp theo trong 60 ngày**

#### **4.4.1. Xác định target và điều kiện gán nhãn**

#### **4.4.2. Huấn luyện và đánh giá**

### **4.5. Tổ chức quy trình huấn luyện trên Microsoft Fabric**

# **CHƯƠNG 5: KHAI THÁC DỮ LIỆU**

### **5.1. Khai thác dữ liệu với Power BI**

#### 5.1.1. Tổng quan hoạt động bán hàng

#### 5.1.2. Phân tích sản phẩm và vận hành giao hàng

#### 5.1.3. Theo dõi hạn ngạch và tồn kho

#### 5.1.4. Theo dõi chất lượng dữ liệu và dữ liệu học máy

### **5.2. Xây dựng Data Agent khai thác Semantic Model**

#### 5.2.1. Kiến trúc ứng dụng và nguồn dữ liệu

#### 5.2.2. Luồng xử lý truy vấn

#### 5.2.3. Kiểm soát an toàn và tính nhất quán

#### 5.2.4. Kết quả thử nghiệm và phạm vi triển khai

# **CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**

### **6.1. Kết quả đạt được**

### **6.2. Ưu điểm của giải pháp**

### **6.3. Hạn chế của dự án**

### **6.4. Hướng phát triển**

**TÀI LIỆU THAM KHẢO**

