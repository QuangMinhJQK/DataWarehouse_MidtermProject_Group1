
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM [silver].INFORMATION_SCHEMA.COLUMNS
WHERE
    (TABLE_SCHEMA = 'stg'
     AND TABLE_NAME IN (
         'stg_sales_person',
         'stg_person'
     ))
    OR
    (TABLE_SCHEMA = 'int'
     AND TABLE_NAME = 'int_sales_person')
ORDER BY
    TABLE_NAME,
    ORDINAL_POSITION;
