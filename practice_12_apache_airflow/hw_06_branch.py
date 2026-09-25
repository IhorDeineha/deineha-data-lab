# Завдання 6 — branching
from datetime import datetime  # для start_date

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task, get_current_context


@dag(
    dag_id="hw_06_branch",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule=None,  # запуск тільки вручну
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)


def hw_06_branch():

    @task()
    def count_rows():
        """Returns the number of rows."""
        print("Rows number is: 4820")
        return 4820

    @task()
    def no_data():
        """No data returned."""
        print("No data returned")

    @task()
    def load_small():
        """Return small volume of data."""
        print("Returned small volume of data")

    @task()
    def load_big():
        """Return big volume of data."""
        print("Returned big volume of data")

    @task.branch()      # вибір гілки за параметром
    def choose_path(rows):
        """Choose a path."""
        if rows == 0:
            return "no_data"
        if rows < 1000:
            return "load_small"
        return "load_big"

    rows = count_rows()
    branch = (choose_path(rows))
    no_data = no_data()
    load_small = load_small()
    load_big = load_big()

    branch >> [no_data, load_small, load_big]       # після розгалуження вибираємо гілку

hw_06_branch()
