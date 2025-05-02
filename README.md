# Data Quality with Airflow
โปรเจคนี้ผู้เขียนต้องการโฟกัสในเรื่องการตรวจสอบคุณภาพของข้อมูล (Data Quality) ด้วยเครื่องมือ Great Expectations และ Common SQL Provider ใน Airflow ซึ่งจะใช้ข้อมูลจาก SQLite database มาทำการตรวจสอบคุณภาพของข้อมูลตามเงื่อนไขที่ผู้เขียนกำหนด จะทำการตรวจสอบคุณภาพของข้อมูลทั้งในระดับตาราง (Table Level) และระดับคอลัมน์ (Column Level)

## Project Overview
**ใส่รูป**

## Specification
**source** : audible_data_transformed.csv\
**destination** : audible_data_for_analytic.db
column	| data_type	| description |
------- | --------- | ----------- |
timestamp | datetime | เวลาที่ซื้อ |
user_id | string | ID ลูกค้า(เอามาคิดTotal Customer) |
country | string | ประเทศ | not be null |
book_id | integer | ID หนังสือ(เผื่อเอามาใช้ในอนาคต) |
book_title | string | ชื่อหนังสือ |
categories | string | หมวดหมู่หนังสือ |
THBprice | float | รายได้(เงินบาทไทย) |

## Expectation
**source** : audible_data_for_analytic.db

**Table Level Check**
table | expectation | success / failure |
----- | ----------- | -------------- |
audible_analytic | has column name to be in list | ✅ |
audible_analytic | has row count between min 1 and max 2000000 | ✅ |

**Column Level Check**
column	| expectation | success / failure |
------- | ----------- | -------------- |
timestamp | has not null values | ✅ |
user_id | has 8 characters and match in list [a-z0-9] characters| ✅ |
country | has not null valuse | ✅ |
book_id | has integer type | ✅ |
book_title | has not null values | ✅ |
categories | has valuse to be in list | ✅ |
categories | has not null values | ❌ |
THBprice | has valuse between min 20 and max 3000 | ❌ |

## Folder Structure and Explaination
```bash
data-quality-with-airflow/
├── assets/                           # โฟลเดอร์สำหรับเก็บรูปภาพต่างๆ ของโปรเจค
├── dags/                             # โฟลเดอร์สำหรับเก็บไฟล์โค้ดของ DAGs ในการรัน Data pipeline บน Airflow
│   ├── gx_data_quality_check.py      # DAGs ของ Great Expectations
│   └── sql_data_quality_check.py     # DAGs ของ Common SQL
│
├── data/                             # โฟลเดอร์สำหรับเก็บไฟล์ข้อมูลที่ใช้สำหรับโปรเจค และผลลัพธ์จากการทำโปรเจค
│   ├── audible_data_transformed.csv  # Source data to transform for analytic data
│   └── audible_data_for_analytic.db  # Data to check for data quality
│
├── logs/                             # โฟลเดอร์สำหรับเก็บ data logging บน Airflow
│
├── include/                          # โฟลเดอร์สำหรับเก็บไฟล์ต่างๆ เพิ่มเติมที่จะรันผ่าน DAGs
│   └── gx/                           # โฟลเดอร์สำหรับไฟล์ต่างๆของ Great Expectations เช่น ไฟล์ expectation suite, ผลลัพธ์ validation เป็นต้น
│
├── plugins/                          # โฟลเดอร์สำหรับ application ต่างๆที่ต้องการรันบน Airflow ผ่าน Dockerfile
│   ├── Dockerfile
│   └── requirements.txt
│
├── .env                              # จัดการข้อมูลอยู่ในรูปตัวแปร ที่ต้องการเก็บเป็นความลับ
└── docker-compose.yaml               # Docker container ที่จะรัน Service แบบทีละหลายตัวบน Airflow
```

## Workflow
_**Technology stack :** Python, SQL, Docker, Apache Airflow, Great Expectations, Common SQL_\
_**Docker-Compose :**_ [docker-compose.yaml]()\
_**DAGs GX script :**_ [gx_data_quality_check.py]()\
_**DAGs SQL script :**_ [sql_data_quality_check.py]()

1. Setup environment
   * Local Airflow บน Docker ซึ่งโครงสร้างโฟล์เดอร์จะตามที่แสดงด้านบน
   * ติดตั้ง Great Expectations และ Common SQL ใน Dokerfile หรือ requirements.txt
2. Airflow
   * รันไฟล์ docker-compose.yaml เพื่อที่จะเข้าไปรัน Data Pipeline บน Local Airflow server
   * Setup conection SQLite เชื่อมกับไฟล์ database (.db)
  
     ![airflow-2025-04-29_222705](https://github.com/user-attachments/assets/cb48c5ac-1ebf-4de7-9036-26e20e928a95)
     
3. Great Expectations
   * ใส่ไฟล์ path สำหรับ setup GX environment ใน DAGs GX script
     ```py
     GX_DATA_CONTEX = "/opt/airflow/include/gx"
     ```
   * สร้างไฟล์ Expectation Suite และกำหนด Expectation ที่จะตรวจสอบคุณภาพข้อมูล
     ```bash
     ├── gx/
         └── expectations/
             ├── columns_validation_suite.json
             └── table_validation_suite.json
     ```
   * รัน DAGs: GX-DATA-QUALITY-CHECK
  
     ![gx-2025-04-28_113901](https://github.com/user-attachments/assets/08fa761b-379d-47ed-8b7f-c215ce0f965f)

   * ตรวจสอบผลการรัน DAGs: GX-DATA-QUALITY-CHECK
     
     ![gx-2025-04-28_114718](https://github.com/user-attachments/assets/d7aac979-839a-407f-bcea-6addc70ba338)
     _data quality check ใน table level_
     
     ![gx-2025-04-28_114957](https://github.com/user-attachments/assets/6e7e3b93-1941-4334-a138-df594e7fb68c)
     _data quality check ใน column level_

     ![gx-2025-04-28_115205](https://github.com/user-attachments/assets/4141bbd7-a61c-4be9-9aa1-44e137891062)
     _ตัวอย่างผล expectation failed ใน column level_

     ![gx-2025-04-28_115304](https://github.com/user-attachments/assets/b4fdaf0c-b930-457a-9837-db90576701c5)
     _ตัวอย่างผล expectation succeeded ใน column level_

4. Common SQL
   * รัน DAGs: COMMON-SQL-DATA-QUALITY-CHECK

     ![sql-2025-04-29_220751](https://github.com/user-attachments/assets/017be0e1-d9c9-45f0-a0f4-2dc9f893570d)

   * ตรวจสอบผลการรัน DAGs: COMMON-SQL-DATA-QUALITY-CHECK

     ![sql-2025-04-29_221637](https://github.com/user-attachments/assets/a5ad6359-0d39-4a73-80d0-5aa4b74921fd)
     _data quality check ใน column level ของ task id: SQL_validate_column_level_

     ![sql-2025-04-29_221459](https://github.com/user-attachments/assets/41e99392-8c7a-481b-bb4c-0cb7064a7a3f)
     _ตัวอย่างผล run task failed ใน column level_
     
     ![sql-2025-04-29_222626](https://github.com/user-attachments/assets/69484119-6a44-46aa-a591-78d66a62099c)
     _ตัวอย่างผล run task succeeded ใน table level_

## References
* ข้อมูลที่ใช้ในโปรเจค Road to Data Engineer 2.0 (2023) จาก [DataTH School](https://school.datath.com/)
* คุณบีท ปุณณ์สิริ บุณยเกียรติ Special Live หัวข้อเรื่อง [DataTH] Data Quality with Apache Airflow [GitHub](https://github.com/punsiriboo/data-quality-with-apache-airflow)
* Great Expectations Suite ที่ใช้ตรวจสอบคุณภาพข้อมูล [Explore Expectations](https://greatexpectations.io/expectations/)
* Common SQL Operator ที่ใช้ตรวจสอบคุณภาพข้อมูล [Common SQL](https://registry.astronomer.io/providers/apache-airflow-providers-common-sql/versions/latest)
