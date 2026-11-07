-- sales_wh


CREATE OR ALTER VIEW dbo.v_monthly_sales AS
SELECT
    dd.[Year] AS order_year,
    dd.[Month] AS order_month,
    dd.MonthName AS month_name,
    COALESCE(dc.CountryRegion, 'Unknown') AS sales_region,
    COUNT(*) AS orders_cnt,
    SUM(Quantity) AS units_sold,
    SUM(SalesTotal) AS revenue
FROM
    dbo.FactSalesOrder  AS fo
INNER JOIN
    dbo.DimDate AS dd
ON
    fo.SalesOrderDateKey = dd.DateKey
LEFT JOIN
    dbo.DimCustomer AS dc
ON
    dc.CustomerKey = fo.CustomerKey
GROUP BY
    dd.[Year],
    dd.[Month],
    dd.MonthName,
    COALESCE(dc.CountryRegion, 'Unknown')
;

GO

SELECT *
FROM dbo.v_monthly_sales
WHERE order_year = 2022
ORDER BY order_month ASC, sales_region ASC;