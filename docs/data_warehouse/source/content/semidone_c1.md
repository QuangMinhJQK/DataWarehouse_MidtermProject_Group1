### **1.1. Bối cảnh thực tế**

Dữ liệu bán hàng được ghi nhận qua từng đơn hàng và dòng sản phẩm, còn người quản lý cần nhìn thấy doanh thu thay đổi ra sao theo thời gian, sản phẩm và khu vực. Để trả lời những câu hỏi đó, dữ liệu giao dịch phải được tổng hợp và đặt trong một cấu trúc có thể tra cứu theo nhiều góc nhìn.  Chaudhuri và Dayal (1997) cho thấy kho dữ liệu phục vụ phân tích cần dữ liệu lịch sử, được tích hợp và tổ chức phù hợp với các truy vấn tổng hợp. 

Adventure Works Cycles là doanh nghiệp giả định trong một tình huống hướng dẫn của Microsoft. Trong tình huống này, dữ liệu giao dịch và thông tin ngoài giao dịch như hạn mức doanh số từ bảng tính đã được tập hợp vào kho dữ liệu quan hệ AdventureWorksDW2019. Microsoft mô tả các hạn chế ở tầng khai thác: báo cáo tĩnh khó cho phép đi sâu vào dữ liệu, người dùng mất thời gian tạo truy vấn do cấu trúc phức tạp và cách tính được viết riêng cho từng báo cáo có thể làm số liệu tổng hợp khác nhau. Tài liệu đánh giá kho dữ liệu này được thiết kế tốt và không có vấn đề lớn ở khâu nạp dữ liệu. Microsoft lựa chọn bổ sung Analysis Services để cải thiện truy vấn và tái sử dụng cách tính. 

Tình huống hướng dẫn bắt đầu từ một kho dữ liệu đã có và tập trung khai thác dữ liệu bằng Analysis Services. Đồ án này sử dụng Adventure Works làm bối cảnh để thực hành thiết kế kho dữ liệu từ các bảng giao dịch của bộ dữ liệu. Công việc bao gồm xác định mức chi tiết của bảng sự kiện, thiết kế các chiều phân tích và thống nhất quy tắc tính chỉ tiêu, nhằm giải quyết hai hạn chế mà tình huống mẫu nêu ra là khó truy vấn theo nhiều góc nhìn và số liệu khác nhau giữa các báo cáo, trước khi kiểm tra kết quả trên báo cáo.

Microsoft Fabric được chọn làm nền tảng triển khai vì tài liệu tổng quan của Microsoft mô tả khả năng nạp, chuyển đổi, lưu trữ, phân tích và báo cáo trong cùng môi trường. Trong đó, mục Warehouse cho phép tổ chức dữ liệu theo cấu trúc phân tích; Microsoft nêu mô hình hình sao và hình tuyết là các trường hợp phù hợp với Fabric Data Warehouse. Trên nền tảng này, đồ án xây dựng kho dữ liệu, quy trình cập nhật, báo cáo Power BI và mô hình dự báo doanh số.

**1.2. Lý do chọn đề tài**

Bài toán bán hàng của Adventure Works Cycles được chọn vì dữ liệu có thể liên kết giao dịch với sản phẩm, khách hàng, thời gian và khu vực. Các mối liên kết này cho phép thiết kế bảng sự kiện, bảng chiều và kiểm tra những chỉ tiêu cụ thể như doanh thu, số lượng bán và số đơn hàng. Nhờ vậy, số liệu trên báo cáo có thể được đối chiếu ngược với dữ liệu nguồn.

Để các chỉ tiêu được tính nhất quán, dữ liệu cần được chuẩn hóa trong một quy trình có thể chạy lại. Fabric cho phép triển khai quy trình đó cùng với kho dữ liệu và lớp báo cáo trong một môi trường. Dự báo doanh số cũng là yêu cầu của đồ án; chuỗi dữ liệu bán hàng đã xử lý trong kho sẽ là đầu vào để xây dựng và đánh giá mô hình dự báo.

Trong phạm vi đồ án môn học, mỗi quyết định thiết kế có thể được kiểm tra bằng kết quả cụ thể: dữ liệu sau xử lý có khớp nguồn hay không, các chỉ tiêu có cho cùng kết quả khi đối chiếu, và quy trình cập nhật có chạy ổn định. Những kết quả này cũng cho thấy các khâu cần điều chỉnh.

**1.3 Mục tiêu dự án**

**1.3.1 Mục tiêu tổng quan**

Mục tiêu tổng quan của dự án là xây dựng giải pháp kho dữ liệu trên nền tảng Microsoft Fabric phục vụ việc tích hợp, quản lý và khai thác dữ liệu bán hàng của Adventure Works Cycles. Giải pháp hướng đến việc tổ chức dữ liệu thành một hệ thống tập trung, nhất quán và thuận tiện cho phân tích đa chiều, từ đó hỗ trợ theo dõi tình hình kinh doanh, đánh giá hiệu quả bán hàng và nhận diện các xu hướng từ dữ liệu lịch sử.

Trên cơ sở kho dữ liệu được xây dựng, dự án kết hợp ứng dụng học máy, tự động hóa quy trình xử lý dữ liệu và trực quan hóa kết quả phân tích nhằm hỗ trợ ra quyết định trong hoạt động bán hàng. Đồng thời, thông qua quá trình triển khai, thử nghiệm và đánh giá, dự án làm rõ khả năng ứng dụng nền tảng Microsoft Fabric trong việc xây dựng một giải pháp dữ liệu xuyên suốt từ tích hợp dữ liệu nguồn đến khai thác thông tin phục vụ nhu cầu kinh doanh.

**1.3.2 Mục tiêu cụ thể**

Để đạt được mục tiêu tổng quan, dự án hướng đến các mục tiêu cụ thể sau:

Thứ nhất, khảo sát, mô tả và phân tích dữ liệu bán hàng của Adventure Works Cycles nhằm xác định cấu trúc dữ liệu, mối quan hệ giữa các bảng và các thông tin cần thiết cho bài toán phân tích. Đồng thời, đánh giá chất lượng dữ liệu, nhận diện các vấn đề về dữ liệu thiếu, trùng lặp hoặc không nhất quán để làm cơ sở xây dựng quy trình xử lý phù hợp.

Thứ hai, xây dựng quy trình tích hợp và xử lý dữ liệu trên nền tảng Microsoft Fabric, bao gồm thu thập, nạp, làm sạch, chuẩn hóa và chuyển đổi dữ liệu. Quy trình này hướng đến việc bảo đảm tính đầy đủ, nhất quán và toàn vẹn của dữ liệu trước khi đưa vào kho dữ liệu phục vụ phân tích và khai thác.

Thứ ba, thiết kế và triển khai kho dữ liệu theo mô hình đa chiều, tổ chức các bảng sự kiện và bảng chiều phù hợp với đặc điểm dữ liệu bán hàng. Kho dữ liệu cần đáp ứng nhu cầu phân tích các chỉ tiêu như doanh thu, số lượng sản phẩm bán ra và số lượng đơn hàng theo những chiều phân tích chủ yếu, bao gồm thời gian, sản phẩm, khách hàng và khu vực bán hàng.

Thứ tư, xây dựng và đánh giá mô hình học máy phục vụ hoạt động bán hàng trên cơ sở dữ liệu đã được xử lý và tổ chức trong kho dữ liệu. Nội dung này tập trung vào khai thác dữ liệu lịch sử để dự báo doanh số, phân tích xu hướng tiêu thụ và xem xét các yếu tố ảnh hưởng đến kết quả bán hàng, qua đó cung cấp thêm cơ sở cho việc lập kế hoạch kinh doanh.

Thứ năm, thiết lập cơ chế tự động hóa quy trình xử lý và cập nhật dữ liệu, bảo đảm các bước tích hợp, chuyển đổi và khai thác dữ liệu được thực hiện theo trình tự thống nhất. Đồng thời, theo dõi trạng thái thực thi và nhận diện lỗi phát sinh nhằm hỗ trợ duy trì hoạt động ổn định của hệ thống.

Thứ sáu, xây dựng các báo cáo và dashboard trực quan phục vụ theo dõi, phân tích và đánh giá tình hình bán hàng. Các báo cáo hướng đến việc thể hiện những chỉ tiêu kinh doanh chủ yếu, hỗ trợ so sánh kết quả giữa các thời kỳ, sản phẩm và khu vực, đồng thời trình bày kết quả dự báo để người sử dụng thuận tiện khai thác thông tin.

Thứ bảy, thử nghiệm và đánh giá giải pháp dựa trên các tiêu chí về chất lượng dữ liệu, tính chính xác của kết quả tổng hợp, hiệu quả truy vấn, khả năng vận hành quy trình tự động và mức độ đáp ứng của mô hình học máy. Trên cơ sở kết quả thực nghiệm, xác định những hạn chế của giải pháp và đề xuất hướng hoàn thiện, mở rộng trong tương lai.

**1.4. Đối tượng và phạm vi dự án**

**1.4.1. Đối tượng dự án**

Đối tượng nghiên cứu của dự án là dữ liệu bán hàng của Adventure Works Cycles và quy trình xây dựng giải pháp kho dữ liệu trên nền tảng Microsoft Fabric phục vụ khai thác dữ liệu này. Dự án tập trung vào các thông tin liên quan đến đơn hàng, chi tiết bán hàng, sản phẩm, khách hàng, thời gian và khu vực bán hàng, cùng với mối quan hệ giữa các đối tượng dữ liệu trong quá trình phân tích.

Dự án nghiên cứu mô hình tổ chức dữ liệu trong kho dữ liệu, quy trình tích hợp và chuyển đổi dữ liệu, phương pháp ứng dụng học máy cho bài toán bán hàng và cơ chế tự động hóa quá trình xử lý. Các báo cáo và dashboard được xây dựng hướng đến nhu cầu sử dụng của bộ phận quản lý và phân tích bán hàng, phục vụ theo dõi kết quả kinh doanh và tham khảo thông tin dự báo.

**1.4.2. Phạm vi dự án**

Về phạm vi dữ liệu, dự án sử dụng dữ liệu Adventure Works được nhóm lựa chọn để triển khai, tập trung vào các bảng liên quan đến hoạt động bán hàng và những bảng nghiệp vụ cần thiết để bổ sung thông tin phân tích. Phạm vi thời gian được giới hạn trong khoảng dữ liệu lịch sử có sẵn của bộ dữ liệu sử dụng. Việc phân tích và đánh giá được thực hiện trên bộ dữ liệu này trong bối cảnh doanh nghiệp giả định.

Về phạm vi xây dựng hệ thống, dự án triển khai quy trình thu thập, nạp, làm sạch, chuẩn hóa và chuyển đổi dữ liệu trên nền tảng Microsoft Fabric. Dữ liệu sau xử lý được tổ chức thành kho dữ liệu theo mô hình đa chiều, gồm các bảng sự kiện và bảng chiều phù hợp với yêu cầu phân tích bán hàng. Đồng thời, dự án thiết lập quy trình tự động hóa việc xử lý và cập nhật dữ liệu theo lịch hoặc kịch bản thử nghiệm.

Về phạm vi phân tích, dự án tập trung vào các chỉ tiêu chủ yếu như doanh thu, số lượng sản phẩm bán ra và số lượng đơn hàng. Các chỉ tiêu được khai thác theo thời gian, sản phẩm, khách hàng và khu vực bán hàng nhằm theo dõi xu hướng, so sánh kết quả và nhận diện những đặc điểm đáng chú ý trong dữ liệu. Kết quả phân tích được thể hiện thông qua các báo cáo và dashboard trực quan.

Về phạm vi học máy, dự án tập trung xây dựng mô hình dự báo doanh số dựa trên dữ liệu lịch sử. Việc lựa chọn phương pháp và mức độ tổng hợp dữ liệu được xác định phù hợp với đặc điểm của bộ dữ liệu và kết quả khảo sát ban đầu. Mô hình được huấn luyện, thử nghiệm và đánh giá nhằm xem xét khả năng cung cấp thông tin tham khảo cho hoạt động lập kế hoạch bán hàng.

Về phạm vi thử nghiệm và đánh giá, dự án kiểm tra chất lượng dữ liệu sau xử lý, tính chính xác của các chỉ tiêu tổng hợp, khả năng truy vấn và mức độ vận hành ổn định của quy trình tự động hóa. Đối với mô hình học máy, việc đánh giá được thực hiện trên dữ liệu kiểm tra theo trình tự thời gian để xem xét mức độ phù hợp của kết quả dự báo. Kết quả thử nghiệm là cơ sở xác định những hạn chế và đề xuất hướng phát triển của giải pháp.

Dự án được triển khai ở quy mô đồ án môn học, tập trung mô phỏng và đánh giá giải pháp trong môi trường thử nghiệm. Các nội dung như vận hành hệ thống ở quy mô doanh nghiệp, tích hợp dữ liệu giao dịch thời gian thực, tối ưu toàn bộ hoạt động sản xuất và quản lý chuỗi cung ứng nằm ngoài phạm vi triển khai của đồ án.


Chaudhuri, S., & Dayal, U. (1997). An overview of data warehousing and OLAP technology. ACM SIGMOD Record, 26(1), 65–74. https://doi.org/10.1145/248603.248616

Microsoft. (n.d.-a). Analysis Services tutorial scenario. Microsoft Learn. https://learn.microsoft.com/en-us/analysis-services/multidimensional-tutorial/analysis-services-tutorial-scenario?view=sql-analysis-services-2025

Microsoft. (n.d.-c). What is Microsoft Fabric? Microsoft Learn. https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview

Microsoft. (n.d.-b). What is Fabric Data Warehouse? Microsoft Learn. https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing
