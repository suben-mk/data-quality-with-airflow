# นำเข้า libraries
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from airflow.utils.dates import days_ago
import pandas as pd
import sqlite3

# กำหนด connection, Path file และ dataset
data_source_path = "/opt/airflow/data/audible_data_transformed.csv"
data_destination_path = "/opt/airflow/data/audible_data_for_analytic1.db"

GX_DATA_CONTEX = "/opt/airflow/include/gx"
SQLITE_CONN_ID = "sqlite_database1"
SQLITE_TABLE = "audible_analytic"
GX_TABLE_SUITE = "table_validation_suite"
GX_COLUMN_SUITE = "columns_validation_suite"

# กำหนด Default arguments
default_args = {
    'owner': 'suben.mk',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': False,
    'retry_delay': False,
    'schedule_interval': '@once',
    'on_success_callback': False,
    'on_failure_callback': False,
}

# สร้าง DAG - Directed Acyclic Graph
with DAG(
    dag_id='GX-DATA-QUALITY-CHECK',
    default_args=default_args,
    description='Pipeline for great expectation data quality check with Airflow',
    tags=['gx-data-quality-check']
) as dag:

    # Task 1: Transform dataset for data analytic
    def transform_for_data_analytic(data_source, data_destination):
        # ingest dataset
        df_ingest = pd.read_csv(data_source)
        # เลือกข้อมูล column เฉพาะที่จะใช้สำหรับการวิเคราะห์
        df_analytic = df_ingest[['timestamp', 'user_id', 'country', 'Book_ID', 'Book_Title', 'Categories', 'THBPrice']]

        # สร้างการเชื่อมต่อไปยังฐานข้อมูล 
        connection = sqlite3.connect(data_destination_path)
        # สร้าง Cursor สำหรับใช้ในการรันคำสั่ง SQL
        cursor = connection.cursor()
        # สร้างตารางใหม่ชื่อว่า `audible_analytic`
        table_stmt = '''
            CREATE TABLE IF NOT EXISTS audible_analytic (
                timestamp DATE NOT NULL, 
                user_id TEXT NOT NULL,
                country TEXT,
                book_id INTEGER NOT NULL,
                book_title TEXT NOT NULL,
                categories TEXT,
                THBprice REAL NOT NULL
            );
        '''
        cursor.execute(table_stmt)
        # เพิ่มข้อมูล dataframe ใน sqlite database 
        df_analytic.to_sql('audible_analytic', con=connection, if_exists='append', index=False)
        connection.close()
        
        print('Complete!! ദ്ദി ˉ͈̀꒳ˉ͈́ )✧')
    
    transform_to_database = PythonOperator(
        task_id="transform_dataset_for_data_analytic",
        python_callable=transform_for_data_analytic,
        op_kwargs={"data_source": data_source_path,
                   "data_destination": data_destination_path,
                   },
    )

    # Task 2: Validate the data using Great Expectations in table level 
    gx_validate_table_level = GreatExpectationsOperator(
        task_id="gx_validate_table_level",
        conn_id=SQLITE_CONN_ID,
        data_context_root_dir=GX_DATA_CONTEX,
        #schema="audible_analytic",
        data_asset_name=SQLITE_TABLE,
        expectation_suite_name=GX_TABLE_SUITE,
        return_json_dict=True,
    )

    # Task 3: Validate the data using Great Expectations in column level 
    gx_validate_column_level = GreatExpectationsOperator(
        task_id="gx_validate_column_level",
        conn_id=SQLITE_CONN_ID,
        data_context_root_dir=GX_DATA_CONTEX,
        #schema="audible_analytic",
        data_asset_name=SQLITE_TABLE,
        expectation_suite_name=GX_COLUMN_SUITE,
        return_json_dict=True,
    )

    # สร้าง Task dependencies
    transform_to_database >> [gx_validate_table_level, gx_validate_column_level]