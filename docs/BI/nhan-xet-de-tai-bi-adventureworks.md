# Nhận xét đề tài BI và bộ câu hỏi quản trị Q1–Q5, Q*

## 1. Phạm vi nhận xét

**Tên đề tài:** *Giải pháp trí tuệ doanh nghiệp đầu cuối hỗ trợ quản trị hoạt động bán hàng tại Adventure Works Cycles*.

Nhận xét này đánh giá mức độ phù hợp giữa tên đề tài, bộ câu hỏi quản trị Q1–Q5 và Q*, dữ liệu AdventureWorks đã sử dụng trong đồ án kho dữ liệu, thiết kế Data Mart, KPI, dashboard và phân tích what-if. Các kết luận được giới hạn trong những trường dữ liệu hiện có; không giả định có thêm dữ liệu chi phí vận hành, phản ứng của khách hàng hoặc dữ liệu thị trường bên ngoài.

Số liệu được đối chiếu trên bộ AdventureWorks 2019 trong repository. Phần kiểm toán Gold và Data Agent dựa trên mã triển khai đầy đủ ở nhánh `minh/warehouse/init-draft`; nhánh `main` tại thời điểm rà soát chưa chứa đầy đủ các đối tượng này. Nhận xét vì vậy phản ánh thiết kế đã có trong repository, không giả định các mart hoặc measure chưa được triển khai.

## 2. Kết luận tổng thể

Bộ đề tài và câu hỏi **phù hợp với một đồ án Business Intelligence đầu cuối**. Chuỗi câu hỏi tạo được mạch phân tích từ mô tả kết quả kinh doanh, chẩn đoán nguyên nhân, so sánh kênh bán, đánh giá nhân viên và lãnh thổ đến mô phỏng phương án điều chỉnh chiết khấu. Q* là điểm nhấn tốt vì chuyển dashboard từ vai trò trình bày số liệu sang hỗ trợ xem xét quyết định.

Để lập luận chặt chẽ, báo cáo cần hoàn thiện ba điểm:

1. Chuẩn hóa định nghĩa KPI và dùng thuật ngữ **doanh thu thuần** thay cho “doanh số thuần” khi chỉ tiêu được tính bằng tiền.
2. Chứng minh thuộc tính kênh Internet/Reseller được bảo toàn từ nguồn đến Data Mart, Semantic Model và dashboard.
3. Trình bày Q* như một mô phỏng kế toán có điều kiện, không diễn giải thành dự báo nhu cầu, tác động nhân quả hoặc phương án tối ưu đã được chứng minh.

## 3. Bằng chứng từ dữ liệu hiện có

### 3.1. Phạm vi giao dịch

| Nội dung | Kết quả đã kiểm tra | Ý nghĩa đối với đề tài BI |
|---|---:|---|
| Đơn hàng | 31.465 | Đủ để phân tích theo thời gian, kênh, khách hàng, nhân viên và lãnh thổ |
| Dòng chi tiết đơn hàng | 121.317 | Cho phép phân tích ở mức sản phẩm, chương trình ưu đãi, số lượng, giá và chiết khấu |
| Khách hàng nguồn | 19.820 | Hỗ trợ chỉ tiêu số khách hàng có mua và số đơn bình quân trên khách hàng |
| Sản phẩm | 504 | Hỗ trợ phân tích sản phẩm, phân nhóm và danh mục |
| Lãnh thổ bán hàng | 10 | Hỗ trợ so sánh khu vực và phân tích Reseller theo lãnh thổ |
| Khoảng ngày đặt hàng | 31/05/2011–30/06/2014 | Cho phép phân tích xu hướng; tháng 05/2011 chỉ có một ngày dữ liệu |

Toàn bộ đơn hàng hiện có mang trạng thái 5, tức trạng thái đã giao theo mã nguồn. Vì vậy, điều kiện chỉ ghi nhận đơn đủ điều kiện doanh thu không làm thay đổi tập lịch sử hiện tại, nhưng vẫn cần giữ trong mô hình để quy tắc có thể áp dụng cho dữ liệu mới.

### 3.2. Kênh bán

Kênh bán được xác định từ `SalesOrderHeader.OnlineOrderFlag`:

| Giá trị nguồn | Nhãn BI đề xuất | Số đơn | Doanh thu dòng hàng | Tỷ trọng doanh thu |
|---|---|---:|---:|---:|
| `1` / `True` | Internet | 27.659 | 29,36 triệu | 26,73% |
| `0` / `False` | Reseller | 3.806 | 80,49 triệu | 73,27% |

Các đơn Internet không có `SalesPersonID`; số giá trị thiếu là 27.659, đúng bằng số đơn Internet. Các đơn Reseller có nhân viên bán hàng và gắn với khách hàng cửa hàng. Do đó, việc giới hạn Q2, Q5 và Q* ở Reseller phù hợp với cấu trúc dữ liệu.

### 3.3. Chiết khấu, giá vốn và quota

| Nguồn dữ liệu | Quy mô/đặc điểm đã kiểm tra | Câu hỏi được hỗ trợ |
|---|---|---|
| `SalesOrderDetail` | Có `UnitPrice`, `OrderQty`, `UnitPriceDiscount`, `LineTotal` và `SpecialOfferID` | Q1, Q2, Q3, Q5, Q* |
| Dòng Reseller có chiết khấu | 3.282 dòng; không có dòng Internet nào có `UnitPriceDiscount > 0` | Q2, Q5, Q* |
| Chương trình chiết khấu Reseller được sử dụng | 11 chương trình có phát sinh dòng bán chiết khấu | Q2, Q* |
| `SpecialOffer` | 16 chương trình trong danh mục nguồn | Q2, Q* |
| `ProductCostHistory` | 395 bản ghi giá vốn chuẩn lịch sử | Q1, Q2, Q5, Q* |
| `SalesPersonQuotaHistory` | 163 bản ghi của 17 nhân viên | Q4 |

`SalesOrderDetail.UnitPriceDiscount` phải là nguồn xác định mức chiết khấu thực tế của dòng bán. `SpecialOffer.DiscountPct` mô tả chương trình và không nên thay thế giá trị thực tế trên dòng giao dịch nếu hai trường khác nhau.

Giá vốn trong dữ liệu là **standard cost lịch sử**, không phải toàn bộ giá vốn kế toán hoặc chi phí thực tế. Vì vậy, mọi chỉ tiêu lợi nhuận phải mang tên “lãi gộp ước tính”, “biên lãi gộp ước tính” hoặc cách gọi tương đương.

## 4. Đánh giá từng câu hỏi quản trị

### Q1 — Xu hướng và đóng góp sản phẩm

**Mức độ phù hợp:** Cao.

Q1 khai thác được `OrderDate`, `LineTotal`, `OrderQty`, cấu trúc sản phẩm–phân nhóm–danh mục, `OnlineOrderFlag` và giá vốn lịch sử. Câu hỏi phù hợp với trang tổng quan điều hành và trang phân tích sản phẩm.

**Điểm cần sửa:** Q1 đang đồng thời hỏi xu hướng thời gian, đóng góp sản phẩm, suy giảm doanh thu và lãi gộp âm. Khi triển khai nên tách thành hai nhóm phân tích:

- Q1a: doanh thu thuần và lãi gộp ước tính biến động theo thời gian và kênh bán.
- Q1b: sản phẩm và danh mục nào đóng góp lớn, suy giảm hoặc có lãi gộp ước tính âm.

“Suy giảm” phải có quy tắc, chẳng hạn so với tháng trước, cùng kỳ năm trước hoặc trung bình trượt. Do tháng 05/2011 chỉ có dữ liệu ngày 31, không nên dùng tháng này để so sánh trực tiếp với một tháng đầy đủ.

### Q2 — Hiệu quả chương trình chiết khấu tại Reseller

**Mức độ phù hợp:** Rất cao.

Dữ liệu cho thấy chiết khấu thực tế chỉ xuất hiện ở kênh Reseller, nên phạm vi câu hỏi phản ánh đúng dữ liệu. Có thể so sánh nhóm không chiết khấu với từng chương trình và sản phẩm bằng doanh thu, tiền chiết khấu, lãi gộp sau chiết khấu và kịch bản không chiết khấu.

**Điểm cần sửa:** “Lãi gộp trước chiết khấu” không phải một kết quả giao dịch thực tế. Nên gọi là:

> Lãi gộp ước tính trong kịch bản không áp dụng chiết khấu, khi giữ nguyên lượng bán, cơ cấu bán, đơn giá trước chiết khấu và giá vốn lịch sử.

Cách gọi này tránh tạo ấn tượng rằng dữ liệu đã quan sát được doanh thu trước và sau cùng một chương trình.

### Q3 — So sánh Internet và Reseller

**Mức độ phù hợp:** Rất cao.

Hai kênh có khác biệt rõ về số đơn, doanh thu, loại khách hàng và sự hiện diện của nhân viên bán hàng. Các KPI doanh thu thuần, số đơn, số khách hàng có mua, AOV và số đơn bình quân trên khách hàng đều có thể tính từ dữ liệu hiện có.

**Điểm cần lưu ý:** Hai nhóm khách hàng không giao nhau trong tập dữ liệu hiện tại. Vì vậy, Q3 là so sánh hai mô hình bán hàng và hai tập khách hàng khác nhau, không phải thí nghiệm trong đó cùng một nhóm khách hàng được phân ngẫu nhiên vào hai kênh. Không nên diễn giải chênh lệch KPI là tác động nhân quả của kênh bán.

### Q4 — Mức hoàn thành chỉ tiêu của nhân viên

**Mức độ phù hợp:** Cao, với điều kiện chuẩn hóa kỳ đối chiếu.

Dữ liệu có 163 bản ghi quota của 17 nhân viên và các đơn Reseller có `SalesPersonID`. Câu hỏi phù hợp với dashboard quản trị lực lượng bán hàng.

**Quy tắc bắt buộc:**

- Chỉ phân bổ doanh thu cho nhân viên từ các đơn có `SalesPersonID`.
- Ghép doanh thu và quota theo cùng một kỳ thời gian.
- Chỉ so sánh các kỳ có đủ dữ liệu doanh thu và quota.
- Công bố rõ ngày bắt đầu, ngày kết thúc và cách xử lý kỳ không đầy đủ.
- Khi phân tích lãnh thổ lịch sử, ghép nhân viên–lãnh thổ theo khoảng hiệu lực, không dùng duy nhất lãnh thổ hiện tại.

### Q5 — Mức độ phụ thuộc vào dòng bán chiết khấu

**Mức độ phù hợp:** Cao.

Q5 bổ sung góc nhìn rủi ro theo nhân viên và lãnh thổ. Dữ liệu đủ để xác định dòng có chiết khấu, doanh thu từ các dòng đó, biên lãi gộp ước tính, AOV và số dòng bình quân mỗi đơn.

**Điểm cần sửa:** Cụm “tỷ trọng doanh số từ các dòng bán có chiết khấu cao” có thể được hiểu là các dòng có *mức chiết khấu cao*. Nên viết:

> Tại kênh Reseller, nhân viên và lãnh thổ nào có **tỷ trọng doanh thu thuần từ các dòng có áp dụng chiết khấu ở mức cao**?

Trong mô hình, dòng có chiết khấu nên được xác định bằng `UnitPriceDiscount > 0`. Q2 tập trung vào chương trình và sản phẩm; Q5 tập trung vào mức độ phơi nhiễm của nhân viên và lãnh thổ. Phân biệt này giúp hai câu không trùng nhau.

### Q* — What-if chiết khấu và ngưỡng hòa vốn

**Mức độ phù hợp:** Rất cao nếu giữ đúng ranh giới mô phỏng.

Q* có thể trả lời bằng phép tính xác định trên dữ liệu giao dịch và giá vốn lịch sử. Các phương án giữ nguyên, giảm hoặc bỏ chiết khấu cho thấy lãi gộp ước tính thay đổi thế nào khi giữ nguyên các yếu tố còn lại.

Q* **không chứng minh** khách hàng sẽ tiếp tục mua cùng số lượng khi chiết khấu thay đổi. Kết quả không phải dự báo nhu cầu, không đo độ co giãn giá và không đủ để kết luận một chương trình nên bị loại bỏ. Cách diễn giải phù hợp là:

> Trong điều kiện lượng bán, cơ cấu bán, đơn giá trước chiết khấu và giá vốn lịch sử không đổi, phương án nào cải thiện lãi gộp ước tính và trường hợp nào vẫn không thể hòa vốn chỉ bằng điều chỉnh chiết khấu?

## 5. Điểm mạnh của thiết kế đề tài

1. **Mạch quản trị rõ:** Q1 mô tả kết quả, Q2 và Q5 chẩn đoán ảnh hưởng của chiết khấu, Q3 so sánh kênh, Q4 đánh giá lực lượng bán hàng, Q* mô phỏng phương án.
2. **Gắn với thiết kế Data Mart:** Mỗi câu hỏi chỉ rõ chiều phân tích và KPI, tạo căn cứ thiết kế fact, dimension, measure và dashboard.
3. **Tận dụng đúng dữ liệu AdventureWorks:** Bộ câu hỏi sử dụng các bảng bán hàng, sản phẩm, ưu đãi, giá vốn, nhân viên, quota và lãnh thổ đã có; không đòi hỏi dữ liệu ngoài phạm vi cho phần tính toán chính.
4. **Có giá trị hỗ trợ quyết định:** Q* tạo lớp phân tích tình huống thay vì dừng ở báo cáo mô tả.
5. **Có ranh giới học thuật phù hợp:** Việc tuyên bố what-if không phải dự báo nhu cầu giúp kết luận tương xứng với bằng chứng.
6. **Phân biệt đúng hai kênh:** Internet và Reseller có cấu trúc nghiệp vụ khác nhau, được xác định trực tiếp từ `OnlineOrderFlag` và được dữ liệu nhân viên/cửa hàng củng cố.

## 6. Điểm yếu và rủi ro

1. **Thuật ngữ doanh số/doanh thu chưa thống nhất:** Khi chỉ tiêu đo bằng tiền nên dùng “doanh thu thuần”; “số lượng bán” dùng cho `OrderQty`.
2. **Kênh bán chưa được chứng minh xuyên suốt trong tài liệu cũ:** EDA và Bus Matrix có đề cập, nhưng mô tả fact, Semantic Model và dashboard phải chỉ ra trường hoặc dimension kênh cụ thể.
3. **Q1 quá rộng:** Một câu hỏi chứa nhiều nhiệm vụ phân tích, dễ tạo dashboard dày đặc và kết luận rời rạc.
4. **Q2 và Q5 có nguy cơ chồng lặp:** Cần giữ Q2 ở cấp chương trình–sản phẩm và Q5 ở cấp nhân viên–lãnh thổ.
5. **Quota cần căn chỉnh kỳ:** Nếu ghép theo năm/tháng không đúng với `QuotaDate`, tỷ lệ hoàn thành có thể sai.
6. **Giá vốn không phủ tuyệt đối mọi dòng:** Dòng không tìm được giá vốn có hiệu lực phải được gắn cờ và loại khỏi KPI lợi nhuận hoặc xử lý bằng chính sách đã công bố; không được ngầm thay bằng 0.
7. **Biên lãi gộp chỉ là ước tính:** Standard cost không gồm đầy đủ chi phí thực tế, thuế, vận chuyển, chi phí bán hàng và chi phí chung.
8. **Rủi ro tiền tệ:** Có 17.489 đơn thiếu `CurrencyRateID`. Báo cáo cần công bố chính sách tiền tệ và không cộng trực tiếp các giá trị khác đơn vị tiền tệ khi chưa chuẩn hóa.
9. **What-if không mô hình hóa phản ứng thị trường:** Giảm hoặc bỏ chiết khấu có thể làm lượng bán thay đổi, nhưng dữ liệu hiện có không cung cấp quan hệ nhân quả để ước lượng thay đổi này.
10. **AdventureWorks là dữ liệu mẫu:** Kết luận chỉ minh họa cách một hệ thống BI hỗ trợ quản trị trong bối cảnh Adventure Works Cycles; không nên khái quát thành hiệu quả đã kiểm chứng tại doanh nghiệp thực tế.

## 7. Bộ định nghĩa KPI đề xuất

### 7.1. Doanh thu và chiết khấu

```text
Gross Sales Amount
= Σ(OrderQty × UnitPrice)

Discount Amount
= Σ(OrderQty × UnitPrice × UnitPriceDiscount)

Net Sales Amount
= Σ[OrderQty × UnitPrice × (1 − UnitPriceDiscount)]
= Σ(LineTotal)
```

`LineTotal` là doanh thu dòng hàng sau chiết khấu, chưa gồm `TaxAmt` và `Freight`. Thuế và phí vận chuyển nằm ở mức đầu đơn và không được cộng lặp vào fact dòng hàng.

### 7.2. Giá vốn và lãi gộp ước tính

```text
Estimated Standard Cost Amount
= Σ(OrderQty × StandardCost có hiệu lực tại OrderDate)

Estimated Gross Profit Amount
= Net Sales Amount − Estimated Standard Cost Amount

Estimated Gross Margin %
= Estimated Gross Profit Amount / Net Sales Amount
```

Các measure tỷ lệ phải trả về rỗng khi mẫu số bằng 0. Dashboard cần hiển thị độ phủ giá vốn cùng KPI lợi nhuận.

### 7.3. Kênh và khách hàng

```text
Sales Channel
= IF(OnlineOrderFlag = 1, "Internet", "Reseller")

Orders
= DISTINCTCOUNT(SalesOrderID)

Buying Customers
= DISTINCTCOUNT(CustomerID trong tập giao dịch)

Average Order Value
= Net Sales Amount / Orders

Orders per Buying Customer
= Orders / Buying Customers
```

### 7.4. Chỉ tiêu bán hàng

```text
Quota Attainment Amount
= Quota Basis Sales Amount − Sales Quota Amount

Quota Attainment %
= Quota Basis Sales Amount / Sales Quota Amount
```

`Quota Basis Sales Amount` phải được định nghĩa rõ là doanh thu nào, theo ngày nào và trong kỳ nào. Không nên dùng một measure doanh thu chung nếu measure đó bao gồm đơn Internet không có nhân viên bán hàng.

### 7.5. What-if chiết khấu

Với một dòng bán có đơn giá trước chiết khấu `UnitPrice`, số lượng `Q`, tỷ lệ chiết khấu mô phỏng `d` và giá vốn chuẩn có hiệu lực `C`:

```text
Scenario Net Sales       = Q × UnitPrice × (1 − d)
Scenario Estimated Cost  = Q × C
Scenario Estimated GP    = Scenario Net Sales − Scenario Estimated Cost
Break-even Net Unit Price = C
```

Nếu `C ≤ UnitPrice`:

```text
Maximum Feasible Discount = 1 − C / UnitPrice
```

Nếu `C > UnitPrice`, không tồn tại tỷ lệ chiết khấu không âm nào giúp dòng bán hòa vốn khi giữ nguyên đơn giá trước chiết khấu. Trường hợp này cần giá bán trước chiết khấu cao hơn hoặc giá vốn thấp hơn.

## 8. Yêu cầu bảo toàn kênh bán đầu cuối

Tài liệu BI nên chứng minh dòng dữ liệu sau:

```text
Sales.SalesOrderHeader.OnlineOrderFlag
    → stg_sales_order_header.online_order_flag
    → int_sales_orders.sales_channel
    → fact.sales_order / fact.sales_order_line
    → Semantic Model[Sales Channel]
    → slicer, KPI, dashboard và what-if
```

Các cổng kiểm tra tối thiểu:

- Chỉ có hai nhãn hợp lệ: Internet và Reseller.
- Tổng số đơn theo hai kênh bằng tổng số đơn toàn bộ.
- Tổng doanh thu theo hai kênh bằng doanh thu toàn bộ trong cùng bộ lọc.
- Đơn Internet không bị gán nhầm nhân viên bán hàng.
- Q2, Q5 và Q* luôn áp dụng bộ lọc Reseller trong measure hoặc ngữ cảnh báo cáo.

## 9. Kiểm toán khả năng phục vụ của tầng Gold hiện tại

### 9.1. Những thành phần Gold đã có

Việc kiểm tra dựa trên các script trong `silver2goldprocess` của nhánh `minh/warehouse/init-draft`, đặc biệt là `Q_B_Create_Gold_Tables.sql`, `Q_E_Create_Business_Views.sql`, `Q_F_Create_Report_Tables.sql` và `Q_G_Create_Gold_Loader.sql`.

Tầng Gold đã lưu được phần lớn dữ liệu cơ sở cần cho bộ câu hỏi:

- `fact.sales_order` giữ khách hàng, lãnh thổ, nhân viên, trạng thái, `online_order_flag`, tiền hàng, thuế, phí vận chuyển và tổng phải thu ở mức đầu đơn.
- `fact.sales_order_line` giữ sản phẩm, chương trình ưu đãi, kênh bán, số lượng, đơn giá, tỷ lệ chiết khấu, doanh thu gộp, tiền chiết khấu, doanh thu thuần, giá vốn chuẩn tại ngày đặt hàng, chi phí chuẩn ước tính, lãi gộp ước tính và trạng thái ghép giá vốn.
- `dim.product`, `dim.territory`, `dim.sales_person`, `dim.special_offer` và `dim.customer` cung cấp các chiều cần cho Q1–Q5.
- `fact.product_cost_history` giữ lịch sử giá vốn; `fact.sales_quota` giữ quota theo nhân viên và quý; `fact.sales_territory_assignment` giữ khoảng hiệu lực phân công nhân viên–lãnh thổ.
- `mart.sales_line_approved` chỉ công bố các trạng thái được chính sách phê duyệt, giới hạn đến ngày nghiệp vụ hoàn chỉnh và bổ sung trạng thái quy đổi tiền tệ.
- `mart.sales_product_day` tổng hợp lượng bán, doanh thu thuần, tiền chiết khấu, doanh thu trước chiết khấu, lãi gộp ước tính, số dòng và số đơn theo ngày–sản phẩm–lãnh thổ–kênh.
- `mart.quota_performance` đã ghép doanh thu thực tế với quota theo nhân viên và quý.
- Các view nghiệp vụ được vật lý hóa vào `rpt.Sales`, `rpt.OrdersHeader`, `rpt.Quota`, `rpt.Offer`, `rpt.CustomerRFM`, `rpt.DataHealth` và các bảng báo cáo khác sau mỗi lần nạp Gold.

Điều này xác nhận `online_order_flag` đã được giữ tới `fact.sales_order`, `fact.sales_order_line`, `mart.sales_product_day` và `rpt.Sales`. Tuy nhiên, trường vẫn ở dạng boolean; nhãn nghiệp vụ Internet/Reseller chưa được chuẩn hóa thành một thuộc tính văn bản trong Gold.

### 9.2. Ma trận mức độ sẵn sàng

Quy ước:

- **Đủ:** Gold đã có cấu trúc và mart trực tiếp phục vụ câu hỏi.
- **Một phần:** dữ liệu gốc đã có trong fact/dimension nhưng còn thiếu mart, measure hoặc quy tắc công bố.
- **Chưa có:** cần bổ sung logic hoặc cấu trúc mới trước khi trả lời có kiểm soát.

| Câu hỏi | Dữ liệu trong Gold | Mart/report hiện tại | Mức sẵn sàng | Khoảng trống chính |
|---|---|---|---|---|
| Q1 | Có thời gian, sản phẩm, danh mục, kênh, doanh thu, lượng bán, chi phí và lãi gộp ước tính | `mart.sales_product_day`, `rpt.Sales` | **Một phần** | Thiếu measure biên lãi gộp, biến động kỳ trước/cùng kỳ, cờ suy giảm và cờ lãi gộp âm |
| Q2 | Có kênh, chương trình, sản phẩm, tiền chiết khấu, doanh thu trước/sau chiết khấu, chi phí và lãi gộp | `mart.offer_performance` chỉ có số dòng, số đơn, doanh thu và tiền chiết khấu | **Một phần** | Mart offer thiếu sản phẩm, kênh, chi phí, lãi gộp sau chiết khấu và kịch bản không chiết khấu |
| Q3 | Có kênh, khách hàng, đơn hàng, doanh thu và lãnh thổ | `rpt.Sales`; `mart.customer_performance` chưa tách theo kênh | **Một phần** | Thiếu số khách hàng có mua và số đơn bình quân/khách hàng theo kênh trong lớp KPI công bố |
| Q4 | Có quota, nhân viên, doanh thu và kỳ quý | `mart.quota_performance`, `rpt.Quota` | **Đủ ở Gold** | Cần xác nhận relationship thời gian và dimension nhân viên trong Semantic Model; chỉ so sánh kỳ đủ dữ liệu |
| Q5 | Fact có đủ nhân viên, lãnh thổ, dòng chiết khấu, lãi gộp và khóa đơn hàng | Chưa có mart chuyên biệt | **Một phần** | Thiếu tỷ trọng doanh thu chiết khấu, AOV và số dòng/đơn theo nhân viên–lãnh thổ |
| Q* | Fact có đủ đơn giá, tỷ lệ chiết khấu, số lượng và giá vốn để mô phỏng | Chưa có mart hoặc bảng scenario | **Chưa có lớp phục vụ** | Thiếu tham số kịch bản, measure lãi gộp theo phương án, chênh lệch, giá hòa vốn và chiết khấu tối đa khả thi |

### 9.3. Kết luận về Gold

Gold hiện tại **không cần thiết kế lại từ đầu**. Mức hạt của `fact.sales_order_line` và các cột đã có đủ làm nền cho Q1–Q5 và Q*. Phần còn thiếu chủ yếu nằm ở lớp phục vụ:

1. Bổ sung mart/measure cho lợi nhuận, khách hàng, chiết khấu và biến động.
2. Chuẩn hóa kênh thành `sales_channel = 'Internet' | 'Reseller'` thay vì chỉ công bố boolean.
3. Tạo mart riêng cho Q2 và Q5 để tránh viết lại logic phức tạp trong từng visual.
4. Tạo lớp scenario xác định cho Q*; không giao việc tính toán kịch bản cho mô hình ngôn ngữ.

### 9.4. Các đối tượng Gold nên bổ sung

| Đối tượng đề xuất | Mức hạt | Mục đích |
|---|---|---|
| `mart.sales_profitability_month` | Tháng–sản phẩm–lãnh thổ–kênh | Q1: xu hướng, đóng góp, biến động và lãi gộp âm |
| `mart.reseller_offer_product_performance` | Kỳ–chương trình–sản phẩm | Q2: doanh thu, tiền chiết khấu, chi phí, lãi gộp sau chiết khấu và kịch bản không chiết khấu |
| `mart.channel_customer_performance` | Kỳ–kênh–lãnh thổ | Q3: doanh thu, đơn, khách hàng có mua, AOV và đơn/khách hàng |
| `mart.reseller_salesperson_territory_risk` | Kỳ–nhân viên–lãnh thổ | Q5: tỷ trọng doanh thu chiết khấu, biên lãi, AOV và dòng/đơn |
| `mart.discount_scenario_base` | Dòng bán hoặc chương trình–sản phẩm–kỳ | Q*: tập đầu vào xác định cho phép mô phỏng nhưng không làm mất mức chi tiết cần đối soát |

## 10. Kiểm toán Data Agent hiện tại

### 10.1. Kiến trúc phù hợp với BI

Data Agent hiện tại có thiết kế phù hợp cho **conversational BI có quản trị**:

```text
Câu hỏi
→ Gemini lập QueryPlan có cấu trúc
→ catalog allow-list và guardrail
→ bộ biên dịch DAX xác định
→ Semantic Model
→ bảng kết quả giới hạn
→ Gemini diễn giải dựa trên kết quả
```

Mô hình ngôn ngữ không tự viết DAX để chạy, không được ghi dữ liệu và chỉ dùng measure/dimension đã công bố. Mỗi truy vấn bị giới hạn tối đa ba measure, hai dimension, sáu filter và 200 dòng. Đây là một điểm mạnh đáng trình bày trong đồ án BI vì Data Agent tái sử dụng cùng Semantic Model với Power BI thay vì tạo một nguồn số liệu riêng.

### 10.2. Data Agent hiện trả lời được gì

Catalog hiện có các dimension thời gian, sản phẩm, danh mục, loại khách hàng, lãnh thổ, quốc gia, kênh online và trạng thái đơn. Các measure bán hàng chính gồm `Net Sales`, `Orders`, `Quantity`, `AOV`, `Discount Rate`, `Cost Coverage` và `Estimated Standard Margin`. Catalog cũng có các measure quota, chất lượng dữ liệu, tồn kho và dự báo.

Với catalog hiện tại, Data Agent có thể trả lời tốt các câu hỏi như:

- Doanh thu thuần, số đơn và AOV theo năm và kênh.
- Top danh mục hoặc sản phẩm theo doanh thu thuần.
- Doanh thu và lãi gộp ước tính theo danh mục, kèm độ phủ chi phí.
- Doanh thu và tỷ lệ chiết khấu theo lãnh thổ với bộ lọc kênh.
- Tổng quota, doanh thu thực tế đối chiếu quota và tỷ lệ hoàn thành theo kỳ, nếu relationship thời gian của bảng Quota đã hoạt động đúng.
- Ngày nghiệp vụ hoàn chỉnh, thời điểm Gold công bố, độ phủ chi phí và số dòng thiếu tỷ giá.

### 10.3. Khoảng trống của Data Agent đối với Q1–Q5 và Q*

| Câu hỏi | Khả năng hiện tại của Agent | Thiếu gì trong catalog/Semantic Model |
|---|---|---|
| Q1 | Trả được doanh thu, lượng bán và lãi gộp theo thời gian/sản phẩm | Chưa có biên lãi gộp, mức biến động, cờ suy giảm và cờ lãi âm |
| Q2 | Không trả lời đầy đủ | Chưa có dimension chương trình ưu đãi và các measure tiền chiết khấu, lãi trước/sau chiết khấu |
| Q3 | Trả được doanh thu, số đơn và AOV theo kênh | Chưa có số khách hàng có mua và số đơn/khách hàng |
| Q4 | Trả được quota tổng hợp theo kỳ | Không công bố dimension nhân viên; tên nhân viên đang bị chặn |
| Q5 | Không trả lời ở mức nhân viên–lãnh thổ | Thiếu dimension nhân viên và các measure tỷ trọng doanh thu chiết khấu, dòng/đơn |
| Q* | Không thực hiện được | QueryPlan chỉ hỗ trợ measure/dimension/filter; chưa có tham số scenario hoặc phép tính what-if xác định |

Hai hạn chế kỹ thuật cần sửa trước khi dùng thuật ngữ Internet/Reseller trong câu hỏi tự nhiên:

1. `sales.channel` đang là boolean với nhãn “Kênh online”. Bộ ép kiểu nhận `online` và `offline`, nhưng chưa nhận trực tiếp `Internet` và `Reseller`.
2. Catalog không có dimension chương trình ưu đãi và dimension nhân viên. Việc chặn tên nhân viên là hợp lý khi ứng dụng dùng shared service principal và chưa có xác thực người dùng/RLS, nhưng khiến Q4 và Q5 không thể drill-down bằng Agent.

Giải pháp ưu tiên là công bố một cột văn bản `sales_channel` trong `rpt.Sales` và Semantic Model. Nếu cần phân tích nhân viên trong demo, có thể công bố mã nhân viên không trực tiếp định danh; chỉ mở tên nhân viên sau khi có kiểm soát quyền phù hợp.

### 10.4. Không nên để Data Agent tự trả lời Q*

Data Agent hiện chỉ biên dịch một tập con DAX từ kế hoạch đã kiểm tra. Cho phép Gemini tự tính mức chiết khấu mới, giá hòa vốn hoặc lãi gộp kịch bản sẽ phá vỡ nguyên tắc “Semantic Model là nguồn chuẩn”.

Q* nên được triển khai theo một trong hai cách:

- **Power BI what-if parameter:** measure kịch bản được định nghĩa sẵn trong Semantic Model; Agent chỉ đọc kết quả của measure đã kiểm tra.
- **Scenario service xác định:** mở rộng `QueryPlan` bằng một action riêng, kiểm tra biên của tham số chiết khấu rồi gọi logic tính toán cố định. Gemini chỉ nhận diện ý định và diễn giải kết quả, không tự tạo công thức.

## 11. Câu hỏi quản trị đề xuất cho Data Agent

### 11.1. Câu hỏi Q6 phù hợp nhất

Có thể bổ sung một câu hỏi xuyên suốt dành cho Data Agent:

> **Q6 — Khi người quản trị phát hiện một KPI bán hàng bất thường trên dashboard, các lát cắt thời gian, kênh bán, danh mục sản phẩm và lãnh thổ nào cần được thu hẹp để xác định nơi tập trung của biến động; đồng thời độ phủ chi phí, tình trạng tỷ giá và độ mới dữ liệu có đủ để sử dụng kết quả hay không?**

| Thành phần | Nội dung |
|---|---|
| Chiều phân tích | Thời gian, kênh bán, danh mục/sản phẩm, lãnh thổ |
| Chỉ số chính | Doanh thu thuần, số đơn, AOV, lãi gộp ước tính, độ phủ chi phí, dòng thiếu tỷ giá, ngày nghiệp vụ hoàn chỉnh |
| Vai trò của Data Agent | Nhận câu hỏi tự nhiên, thực hiện drill-down có giới hạn, trả bảng kết quả và cảnh báo chất lượng |
| Giới hạn diễn giải | Xác định nơi tập trung của chênh lệch; không khẳng định nguyên nhân nhân quả |

Q6 phù hợp với BI hơn một câu hỏi tra cứu đơn lẻ vì nó thể hiện **self-service analytics có quản trị**: dashboard phát hiện tín hiệu, Data Agent hỗ trợ thu hẹp lát cắt, còn Semantic Model bảo đảm mọi câu trả lời dùng cùng định nghĩa KPI.

### 11.2. Kịch bản hội thoại nên dùng làm minh chứng

Một kịch bản demo nên có chuỗi câu hỏi liên tiếp thay vì chỉ một câu hỏi độc lập:

1. “Doanh thu thuần, số đơn và AOV của Internet và Reseller theo năm là bao nhiêu?”
2. “Riêng Reseller năm có doanh thu giảm, danh mục nào đóng góp doanh thu lớn nhất?”
3. “Trong danh mục đó, lãnh thổ nào có tỷ lệ chiết khấu cao nhất?”
4. “Lãi gộp ước tính và độ phủ chi phí của các lát cắt vừa xem là bao nhiêu?”
5. “Dữ liệu hoàn chỉnh đến ngày nào và có bao nhiêu dòng thiếu tỷ giá?”

Chuỗi này chứng minh khả năng duy trì ngữ cảnh hội thoại, drill-down, tái sử dụng measure và gắn cảnh báo chất lượng với kết quả kinh doanh. Câu hỏi 3 cần sửa mapping Reseller; câu hỏi 4 cần measure biên/lợi nhuận phù hợp nếu muốn diễn giải theo tỷ lệ.

### 11.3. Bộ câu hỏi Agent có thể dùng sau khi hoàn thiện catalog

| Mã | Câu hỏi | Giá trị BI |
|---|---|---|
| DA1 | Kênh nào có doanh thu, AOV và số đơn cao hơn trong cùng kỳ? | Hỗ trợ Q3 |
| DA2 | Danh mục và sản phẩm nào đóng góp lớn nhất vào doanh thu và lãi gộp ước tính của từng kênh? | Drill-down Q1 |
| DA3 | Tại Reseller, chương trình nào có tiền chiết khấu lớn nhưng biên lãi gộp ước tính thấp hoặc âm? | Hỗ trợ Q2 |
| DA4 | Nhân viên nào chưa đạt quota trong kỳ và lãnh thổ liên quan có kết quả ra sao? | Hỗ trợ Q4; cần quyền truy cập nhân viên |
| DA5 | Nhân viên–lãnh thổ nào phụ thuộc nhiều vào doanh thu từ dòng chiết khấu? | Hỗ trợ Q5; cần quyền truy cập nhân viên |
| DA6 | Kết quả lợi nhuận đang xem có độ phủ giá vốn và tỷ giá đủ tin cậy không? | Gắn data quality với quyết định |
| DA7 | Nếu chọn một tỷ lệ chiết khấu kịch bản đã được Semantic Model hỗ trợ, lãi gộp ước tính thay đổi bao nhiêu? | Hỗ trợ Q* sau khi có scenario measure |

### 11.4. Điều kiện nghiệm thu Data Agent cho đồ án BI

- Mỗi Q1–Q6 có ít nhất một known-answer test với kỳ và bộ lọc cố định.
- Agent trả cùng số với visual Power BI khi dùng cùng ngữ cảnh lọc.
- `Internet` và `Reseller` được ánh xạ xác định, không phụ thuộc vào suy đoán của LLM.
- Câu hỏi lợi nhuận luôn kèm `Cost Coverage`; câu hỏi quy đổi tiền tệ kèm số dòng thiếu tỷ giá.
- Câu hỏi Q4/Q5 không công bố thông tin nhân viên nếu người dùng không có quyền.
- Agent từ chối yêu cầu tính what-if ngoài measure hoặc scenario action đã được kiểm tra.
- Câu trả lời nêu kỳ, bộ lọc, đơn vị và giới hạn; không đưa ra kết luận nhân quả.

## 12. Gợi ý tổ chức dashboard

| Trang | Câu hỏi chính | Nội dung đề xuất |
|---|---|---|
| Executive Sales Overview | Q1 | Doanh thu, lượng bán, lãi gộp ước tính, biên lãi; xu hướng; đóng góp danh mục; slicer thời gian và kênh |
| Product & Profitability | Q1 | Xếp hạng sản phẩm, đóng góp, suy giảm, lãi gộp âm và độ phủ giá vốn |
| Discount Effectiveness | Q2 | So sánh chương trình với nhóm không chiết khấu, waterfall tiền chiết khấu và lãi gộp, drill-through sản phẩm |
| Channel & Customer | Q3 | Internet so với Reseller về doanh thu, số đơn, khách hàng, AOV và đơn/khách hàng |
| Salesperson Quota | Q4 | Quota, doanh thu đối chiếu, chênh lệch và tỷ lệ hoàn thành theo kỳ |
| Reseller Risk | Q5 | Tỷ trọng doanh thu chiết khấu, biên lãi, AOV và dòng/đơn theo nhân viên–lãnh thổ |
| Discount What-if | Q* | Tham số chiết khấu, lãi gộp theo kịch bản, chênh lệch, ngưỡng hòa vốn và trường hợp không thể hòa vốn chỉ bằng giảm chiết khấu |

## 13. Phiên bản diễn đạt đề xuất cho Q*

> Đối với các chương trình và sản phẩm có lãi gộp ước tính âm tại kênh Reseller, lãi gộp ước tính thay đổi thế nào trong các kịch bản giữ nguyên, giảm hoặc loại bỏ chiết khấu, khi giữ nguyên đơn giá trước chiết khấu, lượng bán, cơ cấu bán và giá vốn chuẩn lịch sử? Trường hợp nào có thể đạt lãi gộp ước tính không âm chỉ bằng điều chỉnh chiết khấu; trường hợp nào vẫn cần đơn giá trước chiết khấu cao hơn hoặc giá vốn thấp hơn; và giá bán thuần trên một đơn vị tại ngưỡng hòa vốn gộp là bao nhiêu?

Đoạn ranh giới nên đặt ngay sau câu hỏi:

> Phân tích what-if là mô phỏng kế toán có điều kiện trên dữ liệu lịch sử. Kết quả không dự báo sự thay đổi của nhu cầu, lượng bán hoặc cơ cấu khách hàng khi chính sách giá và chiết khấu thay đổi, do đó không được xem là bằng chứng nhân quả hoặc phương án tối ưu đã được kiểm chứng.

## 14. Danh sách hoàn thiện trước khi đưa vào báo cáo

- [ ] Thống nhất thuật ngữ “doanh thu thuần”, “số lượng bán” và “lãi gộp ước tính”.
- [ ] Công bố công thức và mức hạt của từng KPI.
- [ ] Giữ `Sales Channel` từ nguồn đến Semantic Model.
- [ ] Tách rõ vai trò Q2 và Q5.
- [ ] Định nghĩa “suy giảm” trong Q1.
- [ ] Định nghĩa kỳ và cơ sở doanh thu đối chiếu quota trong Q4.
- [ ] Công bố điều kiện `UnitPriceDiscount > 0` cho dòng có chiết khấu.
- [ ] Ghép standard cost theo khoảng hiệu lực tại `OrderDate`.
- [ ] Hiển thị độ phủ giá vốn và không thay giá vốn thiếu bằng 0.
- [ ] Công bố chính sách trạng thái đơn và tiền tệ.
- [ ] Đánh dấu tháng biên không đầy đủ trong phân tích xu hướng.
- [ ] Đặt bộ lọc Reseller cố định cho Q2, Q5 và Q*.
- [ ] Kiểm tra đối soát tổng doanh thu giữa fact, Semantic Model và dashboard.
- [ ] Ghi rõ ranh giới không dự báo nhu cầu của Q*.
- [ ] Bổ sung các mart phục vụ Q2, Q3 và Q5 hoặc measure tương đương đã được kiểm thử.
- [ ] Tạo lớp scenario xác định cho Q* trước khi đưa vào Power BI hoặc Data Agent.
- [ ] Chuẩn hóa `sales_channel` thành Internet/Reseller trong Gold và Semantic Model.
- [ ] Bổ sung mapping `Internet`/`Reseller` và dimension chương trình ưu đãi vào semantic catalog.
- [ ] Bổ sung các measure khách hàng, biên lãi, tiền/tỷ trọng chiết khấu và biến động.
- [ ] Quyết định chính sách quyền truy cập dimension nhân viên cho Q4 và Q5.
- [ ] Viết known-answer test đối chiếu Data Agent với Power BI cho từng câu hỏi được công bố.

## 15. Đánh giá cuối cùng

Đề tài có nền tảng dữ liệu và câu chuyện quản trị phù hợp với môn Business Intelligence. Gold hiện tại đã giữ được dữ liệu chi tiết cần thiết, nhưng mới phục vụ hoàn chỉnh Q4; Q1, Q2, Q3 và Q5 còn thiếu một số mart/measure, còn Q* chưa có lớp scenario. Data Agent có kiến trúc tốt cho conversational BI có quản trị và đã trả lời được các câu hỏi tổng hợp cơ bản, nhưng catalog hiện tại chưa đủ cho toàn bộ Q1–Q5 và không nên tự tính Q*. Điểm cần ưu tiên là hoàn thiện hợp đồng KPI, chuẩn hóa Internet/Reseller, bổ sung lớp phục vụ còn thiếu, mở rộng catalog có kiểm soát và dùng Q6 để thể hiện vai trò drill-down hội thoại gắn với chất lượng dữ liệu. Khi các yêu cầu này được đáp ứng, Q1–Q5 có thể đóng vai trò bằng chứng chẩn đoán, Q6 chứng minh khả năng self-service BI và Q* trở thành lớp hỗ trợ xem xét quyết định có điều kiện trên cùng một nền dữ liệu nhất quán.
