-- sales_lh

CREATE OR ALTER VIEW dbo.v_order_totals AS
SELECT
    SalesOrderNumber AS sales_order_number,
    CAST(OrderDate AS DATE) AS order_date,
    EmailAddress AS customer_email,
    COUNT(*) AS lines_cnt,
    ROUND(SUM(Quantity * UnitPrice), 2) AS amount,
    SUM(TaxAmount) AS tax,
    Round(SUM(TaxAmount) + SUM(Quantity * UnitPrice), 2) AS total
FROM
    dbo.sales
GROUP BY
    SalesOrderNumber,
    CAST(OrderDate AS DATE),
    EmailAddress;


GO

SELECT
    sales_order_number,
    order_date,
    customer_email,
    lines_cnt,
    amount,
    tax,
    total
FROM dbo.v_order_totals
WHERE
    lines_cnt >= 5
ORDER BY total DESC, sales_order_number ASC;