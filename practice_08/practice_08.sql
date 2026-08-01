-- Завдання 1. Покупці за країнами

SELECT COUNT(id) as users_count, country
FROM `bigquery-public-data.thelook_ecommerce.users` 
GROUP BY country
ORDER BY users_count DESC
LIMIT 10;


-- Завдання 2. Виторг за категоріями товарів

SELECT 
  pd.category,
  COUNT(oi.id) as items_sold,
  ROUND(SUM(oi.sale_price), 2) as revenue

FROM `bigquery-public-data.thelook_ecommerce.products` as pd
JOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi
ON pd.id = oi.product_id
GROUP BY
  pd.category

ORDER BY revenue DESC;


-- Завдання 3. Замовлення за окремими статусами

SELECT 
  status,
  COUNT(order_id) AS orders_count
  
FROM `bigquery-public-data.thelook_ecommerce.orders` 
WHERE status IN ("Complete", "Shipped")
GROUP BY status;


-- Завдання 4. Продажі по місяцях

SELECT 
  FORMAT_DATE("%Y-%m",DATE(created_at)) AS month,
  COUNT(id) AS items_sold,
  ROUND(AVG(sale_price), 2) AS avg_price

FROM `bigquery-public-data.thelook_ecommerce.order_items` 
WHERE
  EXTRACT(YEAR FROM created_at) IN (2024, 2025) 
GROUP BY
  month
ORDER BY
  month;


-- Завдання 5. Тільки великі категорії

SELECT 
  pd.category,
  ROUND(SUM(oi.sale_price), 2) as revenue

FROM `bigquery-public-data.thelook_ecommerce.products` as pd
JOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi
ON pd.id = oi.product_id
GROUP BY
  pd.category
HAVING revenue > 100000

ORDER BY revenue DESC;


-- Завдання 6. Топ-10 товарів за виторгом

SELECT 
  pd.name AS product_name,
  pd.brand,
  COUNT(oi.id) AS times_sold,
  ROUND(SUM(oi.sale_price), 2) AS revenue

FROM `bigquery-public-data.thelook_ecommerce.order_items`  as oi
JOIN `bigquery-public-data.thelook_ecommerce.products` as pd
ON pd.id = oi.product_id
GROUP BY
  product_name,
  pd.brand

ORDER BY revenue DESC

LIMIT 10;


-- Завдання 7. Відсоток повернень за категоріями

SELECT 
  pd.category,
  COUNT(oi.id) AS total_items,
  COUNTIF(returned_at IS NOT NULL) AS returned_items,
  ROUND((COUNTIF(returned_at IS NOT NULL) / COUNT(oi.id) * 100), 1) AS return_rate_pct


FROM `bigquery-public-data.thelook_ecommerce.order_items`  as oi
JOIN `bigquery-public-data.thelook_ecommerce.products` as pd
ON pd.id = oi.product_id
GROUP BY
  pd.category

ORDER BY
return_rate_pct DESC;


-- Завдання 8. Середній вік покупця за категорією

WITH avg_age_of_category AS (
SELECT 
  pd.category,
  ROUND(AVG(u.age), 1) AS avg_age,
  COUNT(oi.id) AS buyers

FROM `bigquery-public-data.thelook_ecommerce.order_items`  as oi
JOIN `bigquery-public-data.thelook_ecommerce.products` as pd
ON pd.id = oi.product_id
JOIN `bigquery-public-data.thelook_ecommerce.users` as u
ON oi.user_id = u.id

GROUP BY
  pd.category
)

SELECT 
  category,
  buyers,
  avg_age
  
FROM avg_age_of_category
ORDER BY
  avg_age DESC;


-- Завдання 9. Рейтинг місяців за виторгом

SELECT 
  EXTRACT(MONTH FROM o.created_at) AS month,
  ROUND(SUM(oi.sale_price), 2) AS revenue,
  RANK() OVER ( ORDER BY SUM(oi.sale_price) DESC) AS revenue_rank

FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
ON o.order_id = oi.order_id
WHERE 
  EXTRACT(YEAR FROM o.created_at) in (2025)
GROUP BY
  month
ORDER BY revenue_rank;


-- Завдання 10. Приріст виторгу до попереднього місяця

WITH growth_table AS(
  SELECT
  EXTRACT(MONTH FROM o.created_at) AS month,
  ROUND(SUM(oi.sale_price), 2) AS revenue,

FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
ON o.order_id = oi.order_id
WHERE 
  EXTRACT(YEAR FROM o.created_at) in (2025)
GROUP BY
  month
)

SELECT
  month,
  revenue,
  LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
  ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 1) AS growth_pct
FROM 
  growth_table
ORDER BY 
  month;


-- Завдання 11. Топ-3 товари в кожній категорії

SELECT
  p.category,
  p.name AS product_name,
  ROUND(SUM(sale_price), 2) AS revenue,
  ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(sale_price) DESC) AS rank_in_category

FROM `bigquery-public-data.thelook_ecommerce.order_items`  as o
JOIN `bigquery-public-data.thelook_ecommerce.products` as p
ON p.id = o.product_id

GROUP BY
  p.category,
  p.name
QUALIFY rank_in_category <= 3
ORDER BY 
  category,
  rank_in_category;




