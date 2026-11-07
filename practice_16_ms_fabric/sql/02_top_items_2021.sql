-- sales_lh

SELECT TOP 10
    Item AS item,
    COUNT(DISTINCT SalesOrderNumber) AS orders_cnt,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Quantity * UnitPrice), 2) AS revenue
FROM
    dbo.sales
WHERE OrderDate >= '2021-01-01' AND OrderDate < '2022-01-01'
GROUP BY Item
ORDER BY revenue DESC, item ASC;