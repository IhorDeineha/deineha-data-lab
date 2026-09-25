# Завдання 1 — перший пайплайн
from datetime import datetime  # для start_date

from airflow.sdk import dag, task  # основні інструменти Airflow


@dag(
    dag_id="hw_01_pipeline",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)
def hw_01_pipeline():
    "ETL Function"

    @task()
    def extract():
        '''Extract data'''
        SALES = [
            {"store": "Київ", "amount": 1200.0},
            {"store": "Львів", "amount": 850.5},
            {"store": "Одеса", "amount": 430.25},
            {"store": "Київ", "amount": 610.0},
        ]
        print(f"\nNumber of rows in SALES: {len(SALES)}")
        return SALES

    @task()
    def transform(data):
        '''Transform data'''
        total = 0  # повертає сумарне значення тотал
        for amount in data:
            total += amount["amount"]
        print("Total value:", total)

        unique_stores = []  # знаходимо кількість унікальних магазиніва
        for value in data:
            if value["store"] not in unique_stores:
                unique_stores.append(value["store"])
        print("Number of stores", len(unique_stores))

        transformed_data = {
            "total": round(total, 2),
            "stores": len(unique_stores),
            "rows": len(data)
        }
        return transformed_data

    @task()
    def load(transform_data):
        '''Load and print data'''
        print(f"Transformed data:", transform_data)


    data = extract()
    transform_data = transform(data)
    load(transform_data)


hw_01_pipeline()  # без цього рядка DAG не з'явиться

