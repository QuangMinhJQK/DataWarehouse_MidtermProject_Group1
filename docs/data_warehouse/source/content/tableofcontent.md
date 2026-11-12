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

#### 1.5.1. Microsoft Fabric

#### 1.5.2. OneLake và Lakehouse

#### 1.5.3. Fabric Data Factory

#### 1.5.4. Fabric Data Warehouse

#### 1.5.5. Fabric Data Science

#### 1.5.6. Power BI và Web Application

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

#### 2.4.1. Phân tích doanh thu theo kênh bán hàng

#### 2.4.2. Phân tích doanh thu theo nhóm sản phẩm

#### 2.4.3. Phân tích doanh thu theo thời gian

#### 2.4.4. Phân tích khách hàng

#### 2.4.5. Phân tích doanh thu theo khu vực

### **2.6. Xác định yêu cầu dữ liệu cho giải pháp**

#### 2.6.1. Xác định quy trình nghiệp vụ

#### 2.6.2. Xác định mức độ chi tiết dữ liệu

#### 2.6.3. Xác định các chiều phân tích

#### 2.6.4. Xác định các chỉ tiêu đo lường

#### 2.6.5. Xác định yêu cầu dữ liệu cho Machine Learning

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

#### 3.2.4. Tự động hóa quá trình tích hợp dữ liệu

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

#### 3.6.3. Thiết lập Relationships và Hierarchies

#### 3.6.4. Kết nối với Power BI

# **CHƯƠNG 4: XÂY DỰNG MÔ HÌNH HỌC MÁY CHO HOẠT ĐỘNG BÁN HÀNG**

### **4.1. Chuẩn bị dữ liệu cho Machine Learning**

#### 4.1.1. Xác định bài toán dự báo

#### 4.1.2. Xây dựng tập dữ liệu huấn luyện

#### 4.1.3. Tiền xử lý và biến đổi dữ liệu

### **4.2. Xây dựng mô hình dự báo doanh số**

#### 4.2.1. Xác định biến và đặc trưng đầu vào

#### 4.2.2. Huấn luyện mô hình

#### 4.2.3. Tối ưu và lựa chọn mô hình

#### 4.2.4. Đánh giá mô hình dự báo

### **4.3. Xây dựng mô hình dự báo nhu cầu và nguy cơ hết hàng**

#### **4.3.1. Xác định bài toán**

#### **4.3.2. Xây dựng tập dữ liệu huấn luyện**

#### **4.3.3. Huấn luyện mô hình**

#### **4.3.4. Đánh giá mô hình**

### **4.4. Triển khai Machine Learning trên Microsoft Fabric**

#### **4.4.1. Fabric Data Science và Notebooks**

#### **4.4.2. Quản lý thí nghiệm và mô hình**

#### **4.4.3. Lưu trữ kết quả dự báo**

#### **4.4.4. Tích hợp kết quả dự báo vào Data Warehouse**

# **CHƯƠNG 5: TỰ ĐỘNG HÓA VÀ KHAI THÁC DỮ LIỆU**

### **5.1. Tự động hóa quy trình dữ liệu trên Microsoft Fabric**

#### 5.1.1. Cơ chế điều phối Data Pipeline

#### 5.1.2. Lập lịch và kích hoạt quy trình

#### 5.1.3. Tự động cập nhật dữ liệu

#### 5.1.4. Tích hợp kết quả Machine Learning

### **5.2. Kiểm thử và đánh giá quy trình dữ liệu**

#### 5.2.1. Kiểm tra dữ liệu qua các tầng

#### 5.2.2. Kiểm tra chất lượng dữ liệu tại tầng Silver

#### 5.2.3. Kiểm tra tính đúng đắn của mô hình Data Warehouse

#### 5.2.4. Kiểm tra dữ liệu đầu ra của Machine Learning

### **5.3. Khai thác dữ liệu với Power BI**

#### 5.3.1. Dashboard tổng quan hoạt động bán hàng

#### 5.3.2. Dashboard phân tích khách hàng

#### 5.3.3. Dashboard phân tích sản phẩm

#### 5.3.4. Dashboard phân tích doanh thu

#### 5.3.5. Dashboard phân tích khu vực và kênh bán hàng

#### 5.3.6. Dashboard kết quả dự báo

### **5.4. Xây dựng và triển khai Web Application**

#### 5.4.1. Kiến trúc ứng dụng

#### 5.4.2. Tích hợp dữ liệu từ Data Warehouse

#### 5.4.3. Tích hợp kết quả Machine Learning

#### 5.4.4. Triển khai ứng dụng

# **CHƯƠNG 6: THỬ NGHIỆM VÀ ĐÁNH GIÁ GIẢI PHÁP**

### **6.1. Đánh giá Data Warehouse**

#### 6.1.1. Đánh giá tính đầy đủ và nhất quán của dữ liệu

#### 6.1.2. Đánh giá mô hình Star Schema

#### 6.1.3. Đánh giá khả năng truy vấn và khai thác dữ liệu

### **6.2. Đánh giá các mô hình Machine Learning**

#### 6.2.1. Đánh giá mô hình dự báo doanh số

#### 6.2.2. Đánh giá mô hình dự báo nhu cầu và nguy cơ hết hàng

### **6.3. Đánh giá quy trình tự động hóa**

#### 6.3.1. Kết quả thực thi Data Pipeline

#### 6.3.2. Kết quả cập nhật dữ liệu

#### 6.3.3. Kết quả tích hợp Machine Learning

### **6.4. Đánh giá hệ thống báo cáo và Web Application**

#### 6.4.1. Kết quả Dashboard

#### 6.4.2. Kết quả Web Application

#### 6.4.3. Khả năng hỗ trợ hoạt động bán hàng

### 6.5. Đề xuất khai thác dữ liệu cho hoạt động bán hàng

# **CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**

### **7.1. Kết quả đạt được**

### **7.2. Ưu điểm của giải pháp**

### **7.3. Hạn chế của dự án**

### **7.4. Hướng phát triển**

**TÀI LIỆU THAM KHẢO**

**PHỤ LỤC**

### **A. Đường dẫn dự án**

### **B. Mô tả phân công công việc**

### **C. Mức độ đóng góp của các thành viên**

