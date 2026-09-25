# Завдання 4 — Xcom
from datetime import datetime  # для start_date

from airflow.sdk import dag, task, get_current_context  # основні інструменти Airflow

@dag(
    dag_id="hw_04_xcom",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)

def hw_04_xcom():

    @task()
    def prepare_file() -> None:                 # задача для пыдготовки файлу
        """This task prepares data"""
        context = get_current_context()     # отримуємо загальні дані про задачу
        task_instance = context["ti"]       # отримуємо поточний TaskInstance
        task_instance.xcom_push(key="file_name", value="sales_2025_03.csv")     # додаємо значення через Хсом
        task_instance.xcom_push(key="row_count", value=4820)                    # додаємо значення через Хсом
        print("Added two values via Xcom method")

    @task()    # отримуємо дані про файл з Xcom
    def check_file():
        """Read file metadata from XCom"""
        context = get_current_context()
        task_instance = context["ti"]
        file = task_instance.xcom_pull(task_ids="prepare_file", key="file_name")       # отримуємо значення з Хсом
        rows = task_instance.xcom_pull(task_ids="prepare_file", key="row_count")       # отримуємо значення з Хсом
        print("Pulled two values via Xcom method.", f"File name: {file}, rows: {rows}")

    prepare_file() >> check_file()

hw_04_xcom()
