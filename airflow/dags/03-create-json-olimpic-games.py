import json
import requests
import pandas as pd
from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime

# Define default_args
default_args = {
    'owner': 'your_name',
    'start_date': datetime(2024, 9, 1)
}

# Function to get data from the URL
def request_url(**kwargs):
    url = Variable.get("url")  # Use Airflow Variable for URL
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Failed to retrieve data. Status code: {response.status_code}")

# Function to create JSON from the data
def create_json_olympic_games(**kwargs):
    data = kwargs['ti'].xcom_pull(task_ids='get_data')
    total_pages = data['meta']['last_page']
    results_dict = {}

    for page in range(1, total_pages + 1):
        new_url = Variable.get("url").replace("{page_id}", str(page))
        page_data = requests.get(new_url).json()
        events_list = page_data['data']

        for event in events_list:
            sport = event['discipline_name']
            competitors = event['competitors']
            for competitor in competitors:
                country = competitor['country_id']
                category = event['event_name']
                event_entry = {
                    "detailed_event_name": event['detailed_event_name'],
                    "venue_name": event['venue_name'],
                    "result_mark": f"{competitors[0]['result_mark']}-{competitors[1]['result_mark']}",
                    "result_winner": competitor['result_winnerLoserTie'],
                    "competitors": f"{competitors[0]['country_id']}-{competitors[1]['country_id']}"
                }

                key = (country, sport, category)
                if key not in results_dict:
                    results_dict[key] = {
                        "country": country,
                        "sport": sport,
                        "category": category,
                        "events": []
                    }
                results_dict[key]["events"].append(event_entry)

    final_dict = list(results_dict.values())
    return final_dict

# Function to write JSON to a local file (using Airflow Variable for file path)
def write_json_to_local(**kwargs):
    json_data = kwargs['ti'].xcom_pull(task_ids='create_json')
    file_path = Variable.get("local_file_path")  # Use Airflow Variable for local file path
    df = pd.DataFrame(json_data)

    # Write the DataFrame to a JSON file
    df.to_json(file_path, orient = 'split', force_ascii=False, compression = 'infer', index = 'false')
    return file_path

# Function to download JSON from S3 to local using S3Hook
def download_json_from_s3(**kwargs):
    s3_bucket = Variable.get("s3_bucket_name")  # Get the S3 bucket name from Airflow Variable
    s3_key = 'data/olympic_results.json'  # The S3 key (file name in the bucket)
    local_file_path = Variable.get("local_file_path")  # Use Airflow Variable for the local file path

    # Create S3Hook instance
    s3 = S3Hook(aws_conn_id='aws_default')

    # Download the file from S3 and write to local path
    s3.get_key(key=s3_key, bucket_name=s3_bucket).download_file(local_file_path)

# Create the DAG
with DAG(
    '03-create-json-olimpic-games',
    default_args=default_args,
    schedule_interval=None,  # No automatic schedule, manual triggering
    catchup=False
) as dag:

    # Task 1: Get Data from the URL
    get_data = PythonOperator(
        task_id='get_data',
        python_callable=request_url,
        provide_context=True
    )

    # Task 2: Create JSON from the Data
    create_json = PythonOperator(
        task_id='create_json',
        python_callable=create_json_olympic_games,
        provide_context=True
    )

    # Task 3: Write the JSON to S3
    write_json_to_s3 = S3CreateObjectOperator(
        task_id="write_json_to_s3",
        aws_conn_id='aws_default',
        s3_bucket=Variable.get("s3_bucket_name"),  # Use Airflow Variable for S3 bucket name
        s3_key='data/olympic_results.json',
        data="{{ ti.xcom_pull(task_ids='create_json') }}",
        replace=True
    )

    # Task 4: Download JSON from S3 to Local using S3Hook
    write_json_from_s3_to_local = PythonOperator(
        task_id='write_json_to_local',
        python_callable=write_json_to_local,
        provide_context=True
    )

    # Set task dependencies
    get_data >> create_json >> write_json_to_s3 >> write_json_from_s3_to_local
