-- sales_wh

SELECT TOP 10
    fo.CustomerKey AS customer_key,
    CONCAT(dc.FirstName, ' ' , dc.LastName) AS customer_name,
    dc.City AS city,
    dc.CountryRegion AS country_region,
    COUNT(*) AS orders_cnt,
    MIN(dd.DateAltKey) AS first_order_date,
    MAX(dd.DateAltKey) AS last_order_date,
    SUM(fo.SalesTotal) AS total_spent
FROM [dbo].[FactSalesOrder] AS fo
INNER JOIN [dbo].[DimCustomer] AS dc
ON fo.CustomerKey = dc.CustomerKey
INNER JOIN DimDate AS dd
ON fo.SalesOrderDateKey = dd.DateKey
GROUP BY
    fo.CustomerKey,
    dc.FirstName,
    dc.LastName,
    dc.City,
    dc.CountryRegion
ORDER BY
    total_spent DESC, customer_key ASC;