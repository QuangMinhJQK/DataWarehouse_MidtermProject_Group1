-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN A
IF SCHEMA_ID('src') IS NULL EXEC('CREATE SCHEMA src');
GO
IF SCHEMA_ID('dim') IS NULL EXEC('CREATE SCHEMA dim');
GO
IF SCHEMA_ID('fact') IS NULL EXEC('CREATE SCHEMA fact');
GO
IF SCHEMA_ID('mart') IS NULL EXEC('CREATE SCHEMA mart');
GO
IF SCHEMA_ID('ops') IS NULL EXEC('CREATE SCHEMA ops');
GO
IF SCHEMA_ID('ref') IS NULL EXEC('CREATE SCHEMA ref');
GO
IF SCHEMA_ID('ml') IS NULL EXEC('CREATE SCHEMA ml');
GO
IF SCHEMA_ID('agent') IS NULL EXEC('CREATE SCHEMA agent');
GO
CREATE OR ALTER VIEW src.int_product AS
SELECT * FROM [sliver].[int].[int_product];
GO
CREATE OR ALTER VIEW src.int_customer AS
SELECT * FROM [sliver].[int].[int_customer];
GO
CREATE OR ALTER VIEW src.int_sales_orders AS
SELECT * FROM [sliver].[int].[int_sales_orders];
GO
CREATE OR ALTER VIEW src.int_sales_order_lines AS
SELECT * FROM [sliver].[int].[int_sales_order_lines];
GO
CREATE OR ALTER VIEW src.int_product_price_history AS
SELECT * FROM [sliver].[int].[int_product_price_history];
GO
CREATE OR ALTER VIEW src.int_product_cost_history AS
SELECT * FROM [sliver].[int].[int_product_cost_history];
GO
CREATE OR ALTER VIEW src.int_special_offers AS
SELECT * FROM [sliver].[int].[int_special_offers];
GO
CREATE OR ALTER VIEW src.int_special_offer_products AS
SELECT * FROM [sliver].[int].[int_special_offer_products];
GO
CREATE OR ALTER VIEW src.int_inventory_by_location AS
SELECT * FROM [sliver].[int].[int_inventory_by_location];
GO
CREATE OR ALTER VIEW src.int_inventory_by_product AS
SELECT * FROM [sliver].[int].[int_inventory_by_product];
GO
CREATE OR ALTER VIEW src.int_product_stock_status AS
SELECT * FROM [sliver].[int].[int_product_stock_status];
GO
CREATE OR ALTER VIEW src.int_geography AS
SELECT * FROM [sliver].[int].[int_geography];
GO
CREATE OR ALTER VIEW src.int_sales_person AS
SELECT * FROM [sliver].[int].[int_sales_person];
GO
CREATE OR ALTER VIEW src.int_sales_person_quota_history AS
SELECT * FROM [sliver].[int].[int_sales_person_quota_history];
GO
CREATE OR ALTER VIEW src.int_sales_territory_history AS
SELECT * FROM [sliver].[int].[int_sales_territory_history];
GO
CREATE OR ALTER VIEW src.int_currency AS
SELECT * FROM [sliver].[int].[int_currency];
GO
CREATE OR ALTER VIEW src.int_currency_rate AS
SELECT * FROM [sliver].[int].[int_currency_rate];
GO
CREATE OR ALTER VIEW src.stg_sales_territory AS
SELECT * FROM [sliver].[stg].[stg_sales_territory];
GO

IF SCHEMA_ID('rpt') IS NULL EXEC('CREATE SCHEMA rpt');
GO

-- END A
