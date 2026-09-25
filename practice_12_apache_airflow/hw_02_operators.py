# Завдання 2 — оператори
from datetime import datetime  # для start_date

from airflow.sdk import dag  # основні інструменти Airflow
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator



@dag(
    dag_id="hw_02_operators",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)
def hw_02_operators():
    """Use operators"""

    start = EmptyOperator(
        task_id="start")            # додаємо порожній оператор

    show_date = BashOperator(
        task_id="show_date",
        bash_command="date"
    )                               # виклик дати в терміналі

    count_dags = BashOperator(
        task_id="count_dags",
        bash_command="ls /opt/airflow/dags | wc -l",
    )                                   # рахуємо кількість файлів

    def report(store, amount):
        print(store, amount)

    make_report = PythonOperator(
        task_id="make_report",
        python_callable=report,
        op_args=["Київ", 1810.0]
    )                                   # фиклик функції report

    finish = EmptyOperator(
        task_id="finish"
    )                                   # фінішний оператор

    start >> [show_date, count_dags] >> make_report >> finish


hw_02_operators()  # без цього рядка DAG не з'явиться

