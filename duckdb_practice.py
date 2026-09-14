from azure.storage.blob import ContainerClient
from pathlib import Path
import duckdb, os


# SAS-токен видає викладач; у код репозиторію реальний токен не комітьте
SOURCE_SAS = os.environ["SOURCE_SAS"]
source = ContainerClient.from_container_url(SOURCE_SAS)

print("Connected to Azure Storage.\n")

# Creating the list of all csv file names

csv_files = []
for blob in source.list_blobs():

    if blob.name.endswith('.csv'):
        csv_files.append(blob.name)
print("All csv files from Azure Storage:")
print(csv_files, "\n")

# Завдання 1. Створити озеро та зони
# 1.1 Завантажте всі п'ять файлів із контейнера в локальну теку raw/

def reading_csv(file_name):
    '''Read a csv file and save it to the raw directory'''

    file = source.download_blob(file_name).readall()

    path = Path("raw") / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(file)

    print(f"*** Data for the file '{file_name}' downloaded to the raw directory. ***")

# Calling the reading_csv function with our csv files
for csv_file in csv_files:
    reading_csv(csv_file)


# 1.2. Створіть озеро DuckLake з каталогом lake/catalog.ducklake і текою даних lake/data/
# 1.3. Створіть у ньому три схеми: bronze, silver, gold.

con = duckdb.connect()
con.sql("INSTALL ducklake")
con.sql("LOAD ducklake")

os.makedirs("lake", exist_ok=True)
con.sql("ATTACH 'ducklake:lake/catalog.ducklake' AS lake (DATA_PATH 'lake/data/')")
con.sql("USE lake")

for schema in ("bronze", "silver", "gold"):
    con.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")


# Завдання 2. Зона Bronze — сирі дані як є
# 2.1. Створіть таблицю bronze.customers з обох файлів клієнтів одразу.

# Creating a new table for customers.

con.sql("DROP TABLE IF EXISTS bronze.customers")
con.sql("DROP TABLE IF EXISTS bronze.orders")

print("\nCustomers table:")

customers_table = con.sql(f"""
CREATE TABLE IF NOT EXISTS bronze.customers AS 
SELECT *,
regexp_extract(filename, '[^/]+$') AS _source_file,
       now()                              AS _ingested_at
FROM read_csv('raw/customers_*.csv', header = true, filename = true)
""")

print(con.sql("SELECT * FROM bronze.customers LIMIT 10"))
print("Numbers of rows in the 'bronze.customers' table: ", con.sql("SELECT COUNT(*) FROM bronze.customers").fetchone()[0])

# Creating a new table for orders

print("\nOrders table:")

orders_table = con.sql(f"""
CREATE TABLE IF NOT EXISTS bronze.orders AS 
SELECT *,
regexp_extract(filename, '[^/]+$') AS _source_file,
       now()                              AS _ingested_at
FROM read_csv('raw/orders_*.csv', header = true, filename = true)
""")

print(con.sql("SELECT * FROM bronze.orders LIMIT 10"))
print("Numbers of rows in the 'bronze.orders' table: ", con.sql("SELECT COUNT(*) FROM bronze.orders").fetchone()[0])


# Creating a new table for products

print("\nProduct table:")

product_table = con.sql(f"""
CREATE TABLE IF NOT EXISTS bronze.products AS 
SELECT *,
regexp_extract(filename, '[^/]+$') AS _source_file,
       now()                              AS _ingested_at
FROM read_csv('raw/products*.csv', header = true, filename = true)
""")

print(con.sql("SELECT * FROM bronze.products LIMIT 10"))
print("Numbers of rows in the 'bronze.products' table: ", con.sql("SELECT COUNT(*) FROM bronze.products").fetchone()[0])


# Завдання 3. Зона Silver — очищення та злиття

# 3.1. Створіть дві порожні таблиці з явними типами:

con.sql(""" 
CREATE OR REPLACE TABLE silver.customers (
    customer_id   INTEGER,
    full_name     VARCHAR,
    city          VARCHAR,
    segment       VARCHAR,
    registered_at DATE
);
""")

print("Table silver.customers was created.")

con.sql(""" 
CREATE OR REPLACE TABLE silver.orders (
    order_id    INTEGER,
    customer_id INTEGER,
    product_id  INTEGER,
    order_date  DATE,
    quantity    INTEGER,
    amount      DECIMAL(10,2),
    status      VARCHAR
);
""")

print("Table silver.orders was created.\n")


# 3.2. Напишіть функцію merge_customers(source_file)

def merge_customers(source_file):
    con.sql(f"""
    MERGE INTO silver.customers AS t
    USING (
        SELECT DISTINCT ON (customer_id)
               customer_id::INTEGER AS customer_id,
               trim(full_name)      AS full_name,
               upper(left(trim(city), 1)) || lower(substr(trim(city), 2)) AS city,
               lower(trim(segment)) AS segment,
               registered_at::DATE  AS registered_at
        FROM bronze.customers
        WHERE _source_file = '{source_file}'
    ) AS s
    ON t.customer_id = s.customer_id
    WHEN MATCHED THEN UPDATE SET
        full_name = s.full_name, city = s.city,
        segment = s.segment, registered_at = s.registered_at
    WHEN NOT MATCHED THEN INSERT VALUES
        (s.customer_id, s.full_name, s.city, s.segment, s.registered_at)
    """)


# 3.3. Напишіть функцію merge_orders(source_file) за тим самим зразком. Правила очищення:


def merge_orders(source_file):
    con.sql(f"""
    MERGE INTO silver.orders AS t
    USING (
        SELECT DISTINCT ON (order_id)
            order_id::INTEGER AS order_id,
            customer_id::INTEGER AS customer_id,
            product_id::INTEGER AS product_id,
            order_date::DATE  AS order_date,
            quantity::INTEGER AS quantity,
            replace(replace(amount, ' ', ''), ',', '.')::DECIMAL(10,2) AS amount,
            lower(trim(status)) AS status
        FROM bronze.orders
        WHERE _source_file = '{source_file}' 
        AND customer_id::INTEGER IN (SELECT customer_id FROM silver.customers)
        ) AS s
        ON t.order_id = s.order_id
        WHEN MATCHED THEN UPDATE SET
            order_id = s.order_id, customer_id = s.customer_id, product_id = s.product_id,
            order_date = s.order_date, quantity = s.quantity, amount = s.amount, status = s.status
        WHEN NOT MATCHED THEN INSERT VALUES
            (s.order_id, s.customer_id, s.product_id, s.order_date, s.quantity, s.amount, s.status)
    """)

#3.4. Виконайте злиття у визначеному порядку і після кожного кроку виведіть кількість рядків:

# Merging customer tables
merge_customers("customers_2026_01.csv")
print(f"Customer table 'silver.customers' has {con.sql('SELECT COUNT(*) FROM silver.customers').fetchone()[0]} rows after merging 'customers_2026_01.csv'.")
merge_customers("customers_2026_02.csv")
print(f"Customer table 'silver.customers' has {con.sql('SELECT COUNT(*) FROM silver.customers').fetchone()[0]} rows after merging 'customers_2026_02.csv'.")

# Merging orders tables
merge_orders("orders_2026_01.csv")
print(f"Orders table 'silver.orders' has {con.sql('SELECT COUNT(*) FROM silver.orders').fetchone()[0]} rows after merging 'orders_2026_01.csv'.")
merge_orders("orders_2026_02.csv")
print(f"Orders table 'silver.orders' has {con.sql('SELECT COUNT(*) FROM silver.orders').fetchone()[0]} rows after merging 'orders_2026_02.csv'.")


# 3.5. Порахуйте, скільки лютневих замовлень посилаються на неіснуючого клієнта:

# Count number of orphans
month_diff = con.sql("""
SELECT 
    count(DISTINCT order_id) AS orphans
FROM 
    bronze.orders
WHERE _source_file = 'orders_2026_02.csv'
  AND customer_id::INTEGER NOT IN (SELECT customer_id FROM silver.customers);
"""
)

print("\nNumber of orphans for order_id", month_diff.fetchone()[0])

# 3.6. Перевірте ідемпотентність: виконайте merge_orders("orders_2026_02.csv")

# Count number of unique cities
number_of_cities = con.sql(f"""
SELECT 
    COUNT(DISTINCT city) AS cities
FROM 
    silver.customers
""")

print("Number of cities:", number_of_cities.fetchone()[0])

# Count statuses in silver.orders

print("Table of number statuses")
status_numbers = con.sql("""
SELECT 
    status,
    COUNT(*) AS status_numbers
FROM
    silver.orders
GROUP BY 
    status                   
""")

print(status_numbers)


# Завдання 4. Зона Gold — виміри та факти
# 4.1. Створіть вимір gold.dim_customer з колонками customer_key, full_name, city, segment на основі silver.customers.

con.sql("""
CREATE OR REPLACE TABLE gold.dim_customer AS 
SELECT 
    customer_id AS customer_key,
    full_name,
    city,
    segment
FROM 
    silver.customers
""")

print("gold.dim_customer table has:", con.sql("SELECT COUNT(*) FROM gold.dim_customer").fetchone()[0], "rows.")


# 4.2. Створіть вимір gold.dim_product

con.sql("""
CREATE OR REPLACE TABLE gold.dim_product AS 
SELECT 
    product_id AS product_key,
    product_name,
    category,
    price
FROM
    bronze.products
""")

print("gold.dim_product table has:", con.sql("SELECT COUNT(*) FROM gold.dim_product").fetchone()[0], "rows.")


# 4.3. Створіть таблицю фактів gold.fact_sales

con.sql("""
CREATE OR REPLACE TABLE gold.fact_sales AS    
SELECT
    order_id,
    customer_id AS customer_key,
    product_id AS product_key,
    order_date,
    date_trunc('month', order_date)::DATE AS order_month,
    quantity,
    amount
FROM
    silver.orders
WHERE
    status <> 'cancelled'    
""")

print(f"gold.fact_sales table has: {con.sql('SELECT COUNT(*) FROM gold.fact_sales').fetchone()[0]} rows.")


# 4.4. Побудуйте три вітрини і збережіть кожну у файл Parquet:

# Creating gold_revenue_by_city.parquet
con.sql("""
COPY (
    SELECT c.city, count(*) AS orders, sum(f.amount) AS revenue
    FROM gold.fact_sales f
    JOIN gold.dim_customer c USING (customer_key)
    GROUP BY c.city
    ORDER BY revenue DESC
) TO 'gold_revenue_by_city.parquet' (FORMAT PARQUET);
""")

# Creating gold_revenue_by_category.parquet
con.sql("""
COPY (
    SELECT p.category, COUNT(*) AS orders, sum(f.amount) AS revenue
    FROM gold.fact_sales f
    JOIN gold.dim_product p USING (product_key)
    GROUP BY category
    ORDER BY revenue DESC
) TO 'gold_revenue_by_category.parquet' (FORMAT PARQUET);
""")

# Creating gold_revenue_by_month.parquet
con.sql("""
COPY (
    SELECT order_month, COUNT(*) AS orders, sum(amount) AS revenue
    FROM gold.fact_sales 
    GROUP BY order_month
    ORDER BY revenue DESC
) TO 'gold_revenue_by_month.parquet' (FORMAT PARQUET);
""")


print("\nTable gold_revenue_by_city")
print(con.sql("""
    SELECT *
    FROM read_parquet('gold_revenue_by_city.parquet')
"""))

print("Table gold_revenue_by_category")
print(con.sql("""
    SELECT *
    FROM read_parquet('gold_revenue_by_category.parquet')
"""))

print("Table gold_revenue_by_month")
print(con.sql("""
    SELECT *
    FROM read_parquet('gold_revenue_by_month.parquet')
"""))

# Завдання 5. Версії озера
# 5.1. Виведіть перелік версій озера і кількість версій, які створив ваш конвеєр:


print(con.sql("""
SELECT * FROM lake.snapshots();
"""))


# 5.2. Знайдіть у переліку номер версії, що передувала злиттю лютневих замовлень, і виведіть кількість рядків silver.orders на той момент. Очікуване значення — 300.

print("Number of orders for VERSION #55")
print(con.sql("""
    SELECT COUNT(*)
    FROM lake.silver.orders AT (VERSION => 55);
"""))


# Number of files before compaction
files_before = [
    path for path in Path("lake/data").rglob("*")
    if path.is_file()
]

print("Files before:", len(files_before))

# Merge small adjacent files
con.sql("""
    CALL lake.merge_adjacent_files();
""")

# Number of files after compaction
files_after = [
    path for path in Path("lake/data").rglob("*")
    if path.is_file()
]

print("Files after:", len(files_after))
