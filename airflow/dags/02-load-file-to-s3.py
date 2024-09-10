from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from datetime import datetime

# Define your default_args
default_args = {
    'owner': 'your_name',
    'start_date': datetime(2024, 9, 1),
    'retries': 1,
}


# Function to read the local file content
def read_local_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Create a DAG
with DAG(
    '02-load-file-to-s3',
    default_args=default_args,
    schedule_interval=None,  # No automatic schedule, manual triggering
    catchup=False
) as dag:

    # Task to upload a file to S3 using the S3CreateObjectOperator
    create_s3_object = S3CreateObjectOperator(
        task_id="upload_to_s3",
        aws_conn_id='aws_default',  # The AWS connection set up in Airflow
        s3_bucket='airflow-bucket-s3-fps',  # Your target S3 bucket
        s3_key='hello_world.txt',  # S3 key (file path in the bucket)
        data=read_local_file('/home/hello_world.txt'),  # Local file path
    )

# Setting the task in the DAG
create_s3_object
