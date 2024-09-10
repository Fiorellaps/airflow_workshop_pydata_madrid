from airflow import DAG  
from airflow.operators.bash import BashOperator 
from datetime import datetime, date
from airflow.models import Variable
from airflow.utils.dates import days_ago

import os

default_args = {
    'owner': 'ADMIN', # Usuario al que pretenece el DAG
    'start_date': datetime(2022, 12, 1) # date.today(); days_ago(6) # Fecha de comienzo de la programación
    #'email': ['airflow@example.com'],
    #'email_on_failure': False,
    #'email_on_retry': False,
    #'retries': 1,
    #'sla': timedelta(hours=3) # Tiempo máximo de duración del dag
    #'retry_delay': timedelta(minutes=5),
    #'end_date': datetime(2016, 1, 1),
}

dag_args = {
    'dag_id': '01-check-file-dag', # Identificador único
    'schedule_interval': '@daily', # 0 * * * *; None
    'catchup': False, # Si se pone al día con la ejecuciones o no
    'default_args': default_args,
    "doc_md":(
    """
    # 01-check_file_dag

    Comprobar que un fichero existe en la ruta dada. Para ello usamos un BashOperator que ejecuta un script de bash.

    """),
}

with DAG(**dag_args) as dag:
    # Create abslotue path to file and bash script
    base_dag_path = "/mnt/hostpath/airflow/dags"

    file_path = "external_data/*.csv"
    absolute_file_path = os.path.join(base_dag_path, file_path)
    
    bash_file_path = "utiles/check_file.sh"
    absolute_bash_file_path = os.path.join(base_dag_path, bash_file_path)
 
    check_file_task = BashOperator(
        task_id='check_file',
        bash_command='sh ' + absolute_bash_file_path  + ' ' + absolute_file_path 
    )

    check_file_task.doc_md = ("""
    ## Bash Operator
    comprueba si un fichero existe
    """)
