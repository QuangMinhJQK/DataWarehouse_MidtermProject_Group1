-- Read-only preflight. Run in the Silver Lakehouse SQL analytics endpoint.
-- Do not run Gold DDL until these objects and columns match the guide.

SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('int', 'stg')
ORDER BY TABLE_SCHEMA, TABLE_NAME;

SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE (TABLE_SCHEMA = 'int' AND TABLE_NAME IN (
    'int_product', 'int_customer', 'int_sales_orders',
    'int_sales_order_lines', 'int_product_price_history',
    'int_product_cost_history', 'int_special_offers',
    'int_special_offer_products', 'int_inventory_by_location',
    'int_inventory_by_product', 'int_product_stock_status',
    'int_geography', 'int_sales_person',
    'int_sales_person_quota_history', 'int_sales_territory_history',
    'int_currency', 'int_currency_rate'))
   OR (TABLE_SCHEMA = 'stg' AND TABLE_NAME = 'stg_sales_territory')
ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;

SELECT 'int_product' AS source_table, COUNT_BIG(*) AS row_count FROM int.int_product
UNION ALL SELECT 'int_customer', COUNT_BIG(*) FROM int.int_customer
UNION ALL SELECT 'int_sales_orders', COUNT_BIG(*) FROM int.int_sales_orders
UNION ALL SELECT 'int_sales_order_lines', COUNT_BIG(*) FROM int.int_sales_order_lines
UNION ALL SELECT 'int_product_price_history', COUNT_BIG(*) FROM int.int_product_price_history
UNION ALL SELECT 'int_product_cost_history', COUNT_BIG(*) FROM int.int_product_cost_history
UNION ALL SELECT 'int_special_offers', COUNT_BIG(*) FROM int.int_special_offers
UNION ALL SELECT 'int_special_offer_products', COUNT_BIG(*) FROM int.int_special_offer_products
UNION ALL SELECT 'int_inventory_by_location', COUNT_BIG(*) FROM int.int_inventory_by_location
UNION ALL SELECT 'int_inventory_by_product', COUNT_BIG(*) FROM int.int_inventory_by_product
UNION ALL SELECT 'int_product_stock_status', COUNT_BIG(*) FROM int.int_product_stock_status
UNION ALL SELECT 'int_geography', COUNT_BIG(*) FROM int.int_geography
UNION ALL SELECT 'int_sales_person', COUNT_BIG(*) FROM int.int_sales_person
UNION ALL SELECT 'int_sales_person_quota_history', COUNT_BIG(*) FROM int.int_sales_person_quota_history
UNION ALL SELECT 'int_sales_territory_history', COUNT_BIG(*) FROM int.int_sales_territory_history
UNION ALL SELECT 'int_currency', COUNT_BIG(*) FROM int.int_currency
UNION ALL SELECT 'int_currency_rate', COUNT_BIG(*) FROM int.int_currency_rate
UNION ALL SELECT 'stg_sales_territory', COUNT_BIG(*) FROM stg.stg_sales_territory;

SELECT status, COUNT_BIG(*) AS order_count,
       MIN(order_date) AS first_order_date,
       MAX(order_date) AS last_order_date
FROM int.int_sales_orders
GROUP BY status
ORDER BY status;
