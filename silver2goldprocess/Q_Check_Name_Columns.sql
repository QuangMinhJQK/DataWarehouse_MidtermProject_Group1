
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM [silver].INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN (
    'int_sales_person',
    'stg_sales_territory'
)
AND (
    COLUMN_NAME LIKE '%name%'
    OR COLUMN_NAME LIKE '%first%'
    OR COLUMN_NAME LIKE '%last%'
    OR COLUMN_NAME LIKE '%territory%'
)
ORDER BY TABLE_NAME, ORDINAL_POSITION;
