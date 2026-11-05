-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN F
IF OBJECT_ID('rpt.Sales','U') IS NULL
CREATE TABLE rpt.Sales AS
SELECT * FROM mart.sales_line_approved WHERE 1=0;
GO

IF OBJECT_ID('rpt.OrdersHeader','U') IS NULL
CREATE TABLE rpt.OrdersHeader AS
SELECT * FROM mart.order_operations WHERE 1=0;
GO

IF OBJECT_ID('rpt.Stock','U') IS NULL
CREATE TABLE rpt.Stock AS
SELECT * FROM mart.inventory_product_current WHERE 1=0;
GO

IF OBJECT_ID('rpt.Quota','U') IS NULL
CREATE TABLE rpt.Quota AS
SELECT * FROM mart.quota_performance WHERE 1=0;
GO

IF OBJECT_ID('rpt.Price','U') IS NULL
CREATE TABLE rpt.Price AS
SELECT * FROM mart.price_realization WHERE 1=0;
GO

IF OBJECT_ID('rpt.Offer','U') IS NULL
CREATE TABLE rpt.Offer AS
SELECT * FROM mart.offer_performance WHERE 1=0;
GO

IF OBJECT_ID('rpt.CustomerRFM','U') IS NULL
CREATE TABLE rpt.CustomerRFM AS
SELECT * FROM mart.customer_rfm_current WHERE 1=0;
GO

IF OBJECT_ID('rpt.DataHealth','U') IS NULL
CREATE TABLE rpt.DataHealth AS
SELECT * FROM mart.data_health WHERE 1=0;
GO

IF OBJECT_ID('rpt.Forecast','U') IS NULL
CREATE TABLE rpt.Forecast AS
SELECT * FROM agent.forecast WHERE 1=0;
GO
-- END F
