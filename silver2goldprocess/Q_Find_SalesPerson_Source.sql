
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM [silver].INFORMATION_SCHEMA.COLUMNS
WHERE
    COLUMN_NAME IN (
        'business_entity_id',
        'first_name',
        'last_name',
        'full_name',
        'sales_person_name'
    )
ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
