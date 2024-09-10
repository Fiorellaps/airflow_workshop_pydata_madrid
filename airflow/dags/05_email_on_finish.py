from airflow import DAG  
from airflow.operators.bash import BashOperator 
from datetime import datetime, date, timedelta
from airflow.utils.dates import days_ago

from airflow.operators.email_operator import EmailOperator


default_args = {
    'owner': 'ADMIN',
    'start_date': days_ago(6)  # date.today(); days_ago(6) datetime(2022, 12, 1)
}

dag_args = {
    'dag_id': '05-email-on-finish',
    'schedule_interval': '@monthly',
    'catchup': False,
    'default_args': default_args,
    "doc_md":(
    """
    # 05-email-on-finish

    ## DAG PARA COMPROBAR SI EL CSV EXISTE EN LA RUTA DADA

    """),
}

with DAG(**dag_args) as dag:

    # TAREA  success_email
    dest_email = ['fpa@n.net']
    success_email = EmailOperator(
        task_id='send_email',
        to=dest_email,
        subject='La ejecución del dag ' + dag_args['dag_id'] +' correcta', # Asunto
        html_content=f'''<h3>ÉXITO EN LA EJECUCIÓN!!</h3> <p>La ejecución del dag {dag_args['dag_id']} ha acabado correctamente :)</p> ''', # Contenido
        dag=dag
    )

