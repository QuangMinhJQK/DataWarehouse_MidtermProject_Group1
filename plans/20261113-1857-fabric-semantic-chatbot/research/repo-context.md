# Báo cáo khảo sát repo và ngữ cảnh đồ án

## Hiện trạng đã xác minh

- Target `D:\CODE\datawarehouse\DataWarehouse_MidtermProject_Group1\dataagent_fabric` đang trống.
- Báo cáo `docs/data_warehouse/main.pdf` mô tả kiến trúc Azure SQL -> Bronze -> Silver -> Gold Warehouse/Lakehouse -> Semantic Model -> Power BI/Data Agent.
- Trang nội dung 16-17 và 25-32 xem Data Agent là consumer của cùng Semantic Model với Power BI.
- Phần 3.6 về Semantic Model hiện vẫn là placeholder; repo chưa chứng minh semantic model đã deploy.
- Chapters 4-7 mới có mục lục dự kiến, chưa có nội dung đầy đủ.
- Workspace ID đã biết: `d0eaee60-9f3e-47b2-8aee-bbd327ab2062`.
- Chưa có tenant ID, semantic model/dataset ID, external app registration hoặc credential.
- Workspace identity app ID cũ không được mặc định xem là credential cho app bên ngoài.

## Business scope từ báo cáo

- Grain bán hàng: một dòng cho mỗi `SalesOrderDetailID`.
- Measure lõi: doanh thu/net sales, quantity, distinct orders.
- Phân tích theo thời gian, product/category, customer, territory và sales channel.
- Không trộn line sales với header `TotalDue`; tax/freight ở header grain, không lặp theo dòng.
- Các nhánh mở rộng: shipping timeliness, quota, inventory/reorder, forecast và data health.

## Semantic specification dự kiến từ tutorial, chưa phải live truth

- Model: `sm_gold_sales_inventory`.
- Consumption tables: `rpt.Sales`, `rpt.OrdersHeader`, `rpt.Stock`, `rpt.Quota`, `rpt.Price`, `rpt.Offer`, `rpt.CustomerRFM`, `rpt.DataHealth`, `rpt.Forecast`.
- Dimensions: Date, Product, Customer, Territory, SalesPerson, SpecialOffer.
- Measure seed: `Net Sales`, `Orders`, `Quantity`, `AOV`, `Late Shipment Rate`, `Stock Quantity`, `Reorder Products`, `Gold Published At`, `Complete Business Date`, `Inventory Observed At`, `Stock Age Hours`, `Historical Demo Forecast Qty`, `Operational Forecast Qty`.

## Guardrails nghiệp vụ dùng làm prompt và tests

- Net Sales là approved-status line sales sau discount, không gồm tax/freight.
- Estimated margin luôn đi cùng Cost Coverage; thiếu FX thì KPI report-currency phải blank.
- Stock là snapshot; luôn nêu Inventory Observed At/Stock Age Hours, không dùng date slicer như stock history.
- Forecast chỉ dùng một cutoff + horizon; `RECONSTRUCTED` không được mô tả là operational/current.
- Câu trả lời phải nêu kỳ, đơn vị, freshness/completeness và giới hạn khi liên quan.
- Không bịa dữ liệu, không suy diễn nhân quả, không thực hiện write/action.

## Hệ quả cho code plan

- Catalog phải là file cấu hình và cần live-verification trước khi bật chat.
- Tên workspace/model/table/measure không hard-code trong Python.
- Known-answer tests phải đối chiếu Power BI/REST bằng cùng filter context.
- App này thay Data Agent consumer, không thay Gold Warehouse, Semantic Model hay Power BI.

