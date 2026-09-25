# Завдання 7 — scheduling
from datetime import datetime  # для start_date

from airflow.sdk import dag, task, get_current_context


@dag(
    dag_id="hw_07_schedule",  # назва DAG в інтерфейсі
    start_date=datetime(2025, 1, 1),  # з якої дати рахуються запуски
    schedule="*/5 * * * *",  # запуск кожні 5 хв
    max_active_runs=1, # максимум запусків
    catchup=False,  # не доганяти пропущені дати
    tags=["homework"],  # мітка для фільтра у списку
)

# Задача 7.2: Schedule: */5 * * * * Latest Run: 2026-09-24 14:50:23 Next Run: 2026-09-24 14:55:00

def hw_07_schedule():

    @task()
    def heartbeat():            # виводими тип та логічну дату запуску
        """Print schedule and type of run"""
        context = get_current_context()
        logical_date = context["logical_date"]
        run_type = context["dag_run"].run_type
        print(f"logical_date: {logical_date} | run_type: {run_type}")

    heartbeat()

hw_07_schedule()

# Завдання 7.4.
# 0 7 * * 1-5 - будні дні о 7 ранку
# 0 */6 * * * - кожні 6 годин з часу початку
# @hourly кожної години

# Завдання 7.5
# Такий запуск створив 5 нових запусків (данних взагалі не було, бо я все видалив)


