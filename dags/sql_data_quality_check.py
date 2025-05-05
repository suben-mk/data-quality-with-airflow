# นำเข้า libraries
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import (SQLCheckOperator, SQLColumnCheckOperator, SQLValueCheckOperator) 
from airflow.utils.dates import days_ago
import pandas as pd
import sqlite3

# กำหนด connection, Path file และ dataset
data_source_path = "/opt/airflow/data/audible_data_transformed.csv"
data_destination_path = "/opt/airflow/data/audible_data_for_analytic2.db"

SQLITE_CONN_ID = "sqlite_database2"
SQLITE_TABLE = "audible_analytic"

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
    dag_id='COMMON-SQL-DATA-QUALITY-CHECK',
    default_args=default_args,
    description='Pipeline for common-sql data quality check with Airflow',
    tags=['common-sql-data-quality-check']
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

    # Validate the data using Common-SQL in table level
    # Task2 : Validate column name match to set
    validate_table_columns = SQLCheckOperator(
        task_id='SQL_validate_table_columns_match_to_set',
        sql= f'''
                SELECT 
                    COUNT(*) = 7 AS all_columns_exist
                FROM pragma_table_info('{SQLITE_TABLE}')
                WHERE name IN ('timestamp', 'user_id', 'country', 'book_id', 'book_title', 'categories', 'THBprice')
                ;
            ''',
        conn_id=SQLITE_CONN_ID
    )

    # Task3 : Validate count row in between
    validate_table_row = SQLCheckOperator(
        task_id='SQL_validate_table_row_count_to_between',
        sql= f'''
                SELECT 
                    COUNT(*) BETWEEN 1 AND 2000000 AS row_count_check
                FROM {SQLITE_TABLE}
                ;
            ''',
        conn_id=SQLITE_CONN_ID
    )

    # Validate the data using Common-SQL in column level
    # Task4 : Validate column level
    validate_column_level = SQLColumnCheckOperator(
        task_id='SQL_validate_column_level',
        table=SQLITE_TABLE,
        column_mapping={
            'timestamp': {
                "null_check": {"equal_to": 0}
            },
            'country': {
                "null_check": {"equal_to": 0}
            },
            'book_title': {
                "null_check": {"equal_to": 0}
            },
            'categories': {
                "null_check": {"equal_to": 0}  
            },
            'THBprice': {
                "max": {"leq_to": 3000.0},
                "min": {"greater_than": 20.0}
            },
        },
        conn_id=SQLITE_CONN_ID,
    )

    # Task5 : Validate 'book_id' column is INTEGER type
    validate_column_type = SQLValueCheckOperator(
        task_id='SQL_validate_column_type',
        sql= f'''
                SELECT
                    SUM(CASE WHEN name = 'book_id' AND type = 'INTEGER' THEN 1 ELSE 0 END) AS column_type_check 
                FROM pragma_table_info('{SQLITE_TABLE}')
                ;
            ''',
        pass_value=1,
        conn_id=SQLITE_CONN_ID
    )

    # Task6 : Validate 'user_id' column is 8 characters and a-z, 0-9
    validate_column_regex = SQLValueCheckOperator(
        task_id='SQL_validate_column_regex',
        sql= f'''
                SELECT 
                    --SUM(CASE WHEN user_id NOT REGEXP '^[a-z0-9]{8}$' THEN 1 ELSE 0 END) AS column_regex_check
                    SUM(CASE WHEN LENGTH(user_id) != 8 AND user_id NOT GLOB '[a-z0-9]' THEN 1 ELSE 0 END) AS column_regex_check
                FROM {SQLITE_TABLE}
                ;
            ''',
        pass_value=0,
        conn_id=SQLITE_CONN_ID
    )

    # Task7 : Validate 'categories' column match to set
    validate_column_match_to_set = SQLValueCheckOperator(
        task_id='SQL_validate_column_match_to_set',
        sql= f'''
                SELECT 
                    SUM(CASE WHEN categories NOT IN (
                                                        "Business & Careers",
                                                        "Literature & Fiction",
                                                        "Education & Learning",
                                                        "Teen",
                                                        "Mystery, Thriller & Suspense",
                                                        "Children's Audiobooks",
                                                        "History",
                                                        "Relationships, Parenting & Personal Development",
                                                        "Biographies & Memoirs",
                                                        "Science Fiction & Fantasy",
                                                        "Arts & Entertainment",
                                                        "Health & Wellness",
                                                        "Religion & Spirituality",
                                                        "Erotica",
                                                        "Science & Engineering",
                                                        "Home & Garden",
                                                        "Money & Finance",
                                                        "Romance",
                                                        "Computers & Technology",
                                                        "Politics & Social Sciences",
                                                        "Sports & Outdoors",
                                                        "LGBTQ+",
                                                        "Travel & Tourism")
                                                        THEN 1 ELSE 0 END) AS column_match_set_check
                FROM {SQLITE_TABLE}
                ;
            ''',
        pass_value=0,
        conn_id=SQLITE_CONN_ID
    )    

    # สร้าง Task dependencies
    transform_to_database >> \
    [validate_table_columns,
     validate_table_row,
     validate_column_level,
     validate_column_type,
     validate_column_regex,
     validate_column_match_to_set]