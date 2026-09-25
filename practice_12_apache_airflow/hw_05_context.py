# Завдання 5 — context
from datetime import datetime  # для start_date

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task, get_current_context


@dag(
    dag_id="hw_05_context",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)

def hw_05_context():

    @task()
    def show_context():
        """Getting values from context module"""
        context = get_current_context()             #  звертаємося до данних в contex
        dag_value = context["dag"].dag_id                  # отримуємо дані про dag
        ti = context['ti'].task_id                          # отримуємо дані про task instance
        dag_run = context['dag_run'].run_type               # отримуємо дані про тип запуску
        logical_date = context['logical_date']              # отримаємо дату
        print(f"dag: {dag_value}, ti: {ti}, dag_run:{dag_run}, logical_date: {logical_date}")



    bash_date = BashOperator(
        task_id="echo_date",
        bash_command = "echo {{ ds }}"
    )               # прінтимо дату зі змінною jinja

    @task()     # будуємо шлях зі змінною контекст
    def build_path():
        """Building path"""
        context = get_current_context()
        logical_date = context['logical_date']

        if logical_date is None:
            logical_date = datetime.now()

        logical_date = logical_date.strftime("%Y-%m-%d")

        path = f"/data/sales/{logical_date}.csv"
        print(f"The whole path: {path}")




    show_context() >> bash_date >> build_path()

hw_05_context()
