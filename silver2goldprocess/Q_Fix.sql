
CREATE OR ALTER VIEW src.int_sales_territory AS
SELECT
    territory_id,
    name AS territory_name,
    country_region_code,
    territory_group,
    sales_ytd,
    sales_last_year,
    cost_ytd,
    cost_last_year,
    modified_date
FROM [silver].[stg].[stg_sales_territory];
GO

SELECT TOP (5)
    territory_id,
    territory_name,
    country_region_code,
    territory_group
FROM src.int_sales_territory;


SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dim'
  AND TABLE_NAME IN ('territory', 'sales_person')
ORDER BY TABLE_NAME, ORDINAL_POSITION;

