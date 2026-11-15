
CREATE OR ALTER VIEW src.int_product AS
SELECT * FROM [silver].[int].[int_product];
GO

CREATE OR ALTER VIEW src.int_customer AS
SELECT * FROM [silver].[int].[int_customer];
GO

CREATE OR ALTER VIEW src.int_sales_orders AS
SELECT * FROM [silver].[int].[int_sales_orders];
GO

CREATE OR ALTER VIEW src.int_sales_order_lines AS
SELECT * FROM [silver].[int].[int_sales_order_lines];
GO

CREATE OR ALTER VIEW src.int_product_price_history AS
SELECT * FROM [silver].[int].[int_product_price_history];
GO

CREATE OR ALTER VIEW src.int_product_cost_history AS
SELECT * FROM [silver].[int].[int_product_cost_history];
GO

CREATE OR ALTER VIEW src.int_special_offers AS
SELECT * FROM [silver].[int].[int_special_offers];
GO

CREATE OR ALTER VIEW src.int_special_offer_products AS
SELECT * FROM [silver].[int].[int_special_offer_products];
GO

CREATE OR ALTER VIEW src.int_inventory_by_location AS
SELECT * FROM [silver].[int].[int_inventory_by_location];
GO

CREATE OR ALTER VIEW src.int_inventory_by_product AS
SELECT * FROM [silver].[int].[int_inventory_by_product];
GO

CREATE OR ALTER VIEW src.int_product_stock_status AS
SELECT * FROM [silver].[int].[int_product_stock_status];
GO

CREATE OR ALTER VIEW src.int_geography AS
SELECT * FROM [silver].[int].[int_geography];
GO

CREATE OR ALTER VIEW src.int_sales_person AS
SELECT * FROM [silver].[int].[int_sales_person];
GO

CREATE OR ALTER VIEW src.int_sales_person_quota_history AS
SELECT * FROM [silver].[int].[int_sales_person_quota_history];
GO

CREATE OR ALTER VIEW src.int_sales_territory_history AS
SELECT * FROM [silver].[int].[int_sales_territory_history];
GO

CREATE OR ALTER VIEW src.int_currency AS
SELECT * FROM [silver].[int].[int_currency];
GO

CREATE OR ALTER VIEW src.int_currency_rate AS
SELECT * FROM [silver].[int].[int_currency_rate];
GO

CREATE OR ALTER VIEW src.stg_sales_territory AS
SELECT * FROM [silver].[stg].[stg_sales_territory];
GO


SELECT TOP (5) *
FROM src.int_product;
