-- sales_wh


SELECT
    'DimProduct' AS table_name,
    COUNT(*) AS rows_cnt
FROM [dbo].[DimProduct]

UNION ALL

SELECT
    'DimCustomer',
    COUNT(*)
FROM [dbo].[DimCustomer]

UNION ALL

SELECT
    'DimDate',
    COUNT(*)
FROM [dbo].[DimDate]

UNION ALL

SELECT
    'FactSalesOrder',
    COUNT(*)
FROM [dbo].[FactSalesOrder]

ORDER BY table_name