# Завдання 3 — parallel
from datetime import datetime  # для start_date

from airflow.sdk import dag, task  # основні інструменти Airflow


@dag(
    dag_id="hw_03_parallel",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)

def hw_03_parallel():

    @task()                     # функція початку
    def start():
        print("The task 'start' is called.")

    @task()                     # функція продажів
    def load_sales():
        print("The task 'load_sales' is returning sales data.")
        return 1200

    @task()                     # функція магазинів
    def load_stores():
        print("The task 'load_stores' is returning stores data.")
        return 15

    @task()                     # функція продуктів
    def load_products():
        print("The task 'load_products' is returning products data.")
        return 340

    @task()
    def summarise(sales, stores, products):
        print(f"Total of numbers: {sales + stores + products}")

    start_task = start()
    sales = load_sales()
    stores = load_stores()
    products = load_products()

    start_task >> [sales, stores, products]
    summarise(sales, stores, products)

hw_03_parallel()



