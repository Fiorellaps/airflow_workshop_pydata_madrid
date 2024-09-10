from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define default arguments
default_args = {
    'owner': 'your_name',
    'start_date': datetime(2024, 9, 1)
}

# Create the DAG
with DAG(
    '04-launch-fastapi-dag',
    default_args=default_args,
    schedule_interval=None,  # Manual triggering
    catchup=False
) as dag:
    # Task to kill uvicorn on port 8000 if existing
    kill_uvicorn = BashOperator(
        task_id='kill_uvicorn',
        bash_command="sudo su && pkill -f 'uvicorn'",
        execution_timeout=None  # No timeout since it needs to ensure the kill
    )

    # Task: Launch FastAPI using uvicorn
    launch_fastapi = BashOperator(
        task_id='launch_fastapi',
        bash_command='cd /home/ec2-user/fast_api && nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload &',
        execution_timeout=None  # Disable timeout to keep FastAPI running
    )

# Task to launch FastAPI
kill_uvicorn >> launch_fastapi
