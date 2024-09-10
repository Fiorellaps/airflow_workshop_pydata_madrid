[<img align="left" src="https://raw.githubusercontent.com/PyDataMadrid/.github/main/profile/pydata-madrid-meetup-main.png" alt="español" width="150"/>](https://pydata.org/madrid2016/venue/index.html)

[<img align="right" src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="inglés" width="47"/>](https://www.linkedin.com/in/fiorella-piriz-sapio-74569a188/)

<br/>
<br/>

# Workshop de Airflow PyData Madrid

# 1. Instalación de Airflow en Linux

(Se recomienda instalarlo en una máquina virtual de Linux, en docker o en Kubernetes, más información en la [documentación oficial](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html))

- Creamos un entorno de Python con virtualenv y lo activamos

```python
>!python -m venv airflow_env
>source airflow_env/bin/ativate
```

- Definimos **AIRFLOW_HOME**

```python
>export AIRFLOW_HOME=/home/airflow
```

- Instalamos airflow desde Pypi

```python
!pip install "apache-airflow[amazon]"
```

<div style="color:green">Airflow ofrece muchos más <a href="https://airflow.apache.org/docs/#providers-packagesdocsapache-airflow-providersindexhtml">providers</a>.
    
    
</div>

- Modificar la configuración de airflow

```python
>nano /root/airflow/airflow.cfg
- load_examples=False
- sql_alchemy_conn = postgresql+psycopg2://user:pass@localhost:5432/airflow_db (recomendado en producción)
```

- Comprobamos que está bien instalado

```python
airflow version
```

- Arrancamos airflow manualmente
<div style="color:green">** También se podría arrancar usando el comando `airflow standalone` o en modo cluster
</div>

# 2. Arrancar Airflow

## 1.1. Base de datos (Postgres, SQLite, etc.)

<div style="color:green">
** Más información en https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html
</div>

##### PREPARAR EL POSTGRES (OPCIONAL)

<div style="color:orange">
    
- su - postgres; psql; \l (show databases); \du (show users)
    
- CREATE DATABASE airflow_db;

- CREATE USER airflow_user WITH PASSWORD 'XXX';
- GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;
- ALTER ROLE airflow_user SET search_path = public;

</div>

##### INICIALIZAR POSTGRES

<div style="color:orange">
> airflow db init 
</div>

##### CREAR USUARIO

<div style="color:orange">
> airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@admin.org 
</div>

##### COMPROBAR USUARIO

<div style="color:orange">
> airflow users list 
</div>

## 1.2. Webserver

<div style="color:orange">
> airflow webserver --port 9090
</div>

## 1.3. Scheduler

<div style="color:orange">
> airflow scheduler
</div>

# 3. DAGS

## 01-check-file-dag

Comprobar que un fichero existe en la ruta dada. Para ello usamos un **BashOperator** que ejecuta un script de bash.

Con este DAG aprenderemos:

<div style="color:orange">
    
    
- Configurar Dags: parámetro, intervalos, programación...

- Visualización de Dags en la web: Ver programación, estado del DAG, historial, logs...

- Añadir markdown en DAG y las tareas (instance details).

- BashOperator.

 </div>

```python
BashOperator(
    task_id='check_file',
    bash_command='sh ' + absolute_bash_file_path  + ' ' + absolute_file_path
)
```

- Default args:

Hay muchos más argumentos que se pueden ver en https://airflow.apache.org/docs/apache-airflow/1.10.2/code.html#airflow.models.BaseOperator

- Schedule times

Más información en https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timetable.html

## 02-load-file-to-s3.py

Subir un fichero (en este caso csv) a un bucket de **AWS S3**.

Con este DAG aprenderemos:

<div style="color:orange">
    
    
- S3CreateObjectOperator.

- Configuración de conexiones.

 </div>

```python
create_s3_object = S3CreateObjectOperator(
        task_id="upload_to_s3",
        aws_conn_id='aws_default',  # The AWS connection set up in Airflow
        s3_bucket='airflow-bucket-s3-fps',  # Your target S3 bucket
        s3_key='hello_world.txt',  # S3 key (file path in the bucket)
        data=read_local_file('/home/hello_world.txt'),  # Local file path
)
```

Más información sobre dependencia de tareas https://docs.astronomer.io/learn/managing-dependencies

## 03-create-json-olimpic-games

Acceder a la API de los juegos olímpicos https://apis.codante.io/olympic-games/events, transformar los datos para generar un diccionario de países, deporte y categoría, y finalmente escribir los datos en bucket de S3 y en local.

<div style="color:orange">

- PythonOperator.

- Configuración de variables.
  
- Dependencia de tareas.
  
- Empleo de Hooks.

 </div>

```python
create_json = PythonOperator(
        task_id='create_json',
        python_callable=create_json_olympic_games,
        provide_context=True
)
```

Más información sobre el operador de Amazon [https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/index.html](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html)

## 04-launch-fastapi-dag

Comando de bash para matar los procesos arrancados usando FastAPI y otro para arranacar la API que usa los datos generados en el DAG anterior.

<div style="color:orange">

- BashOperator.

 </div>

```python
launch_fastapi = BashOperator(
        task_id='launch_fastapi',
        bash_command='cd /home/ec2-user/fast_api && nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload &',
        execution_timeout=None  # Disable timeout to keep FastAPI running
)
```


## 05-email-on-finish

Enviar un correo

<div style="color:orange">

- EmailOperator.

[Guía](https://hevodata.com/learn/airflow-emailoperator/) para configurar el envío de correos con una cuenta de GMAIL

 </div>

```python
EmailOperator(
        task_id='send_email',
        to=dest_email,
        subject='La ejecución del dag ' + dag_args['dag_id'] +' correcta',
        html_content=f'''<h3>ÉXITO EN LA EJECUCIÓN!!</h3> <p>La ejecución del dag {dag_args['dag_id']} ha acabado correctamente :)</p> ''',
        dag=dag
)
```
