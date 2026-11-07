-- sales_wh

select [rows].[SalesOrderDateKey] as [SalesOrderDateKey],
    sum([rows].[Quantity]) as [units_sold]
from
(
    select [$Outer].[SalesOrderDateKey],
        [$Outer].[Quantity]
    from [sales_wh].[dbo].[FactSalesOrder] as [$Outer]
    where exists
    (
        select 1
        from
        (
            select [_].[ProductKey] as [ProductKey2]
            from [sales_wh].[dbo].[DimProduct] as [_]
            where [_].[Category] = 'Mountain Bikes' and [_].[Category] is not null
        ) as [$Inner]
        where [$Outer].[ProductKey] = [$Inner].[ProductKey2]
    )
) as [rows]
group by [SalesOrderDateKey]