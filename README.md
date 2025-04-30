# Data Quality with Airflow
โปรเจคนี้ผู้เขียนต้องการตรวจสอบคุณภาพของข้อมูล (Data Quality) ด้วยเครื่องมือ Great Expectations และ Common SQL Provider ใน Airflow ซึ่งจะใช้ข้อมูลจาก SQLite database มาทำการตรวจสอบคุณภาพของข้อมูลตามเงื่อนไขที่ผูเขียนกำหนด จะทำการตรวจสอบคุณภาพของข้อมูลในระดับตาราง (Table Level) และระดับคอลัมน์ (Column Level)

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
table | expectation | success / fial |
----- | ----------- | -------------- |
audible_analytic | has column name to be in list | ✅ |
audible_analytic | has row count between min 1 and max 2000000 | ✅ |

**Column Level Check**
column	| expectation | success / fial |
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
│   └── audible_data_for_analytic.db  # Data to chack for data quality
│
├── logs/                             # โฟลเดอร์สำหรับเก็บ data logging บน Airflow
│
├── include/                          # โฟลเดอร์สำหรับเก็บไฟล์โค้ด python function เพิ่มเติมที่จะรันผ่าน Dags
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
   * ใส่ไฟล์ path สำหรับ set up a GX environment ใน DAGs GX script
     ```py
     GX_DATA_CONTEX = "/opt/airflow/include/gx"
     ```
   * สร้างไฟล์ Expectation Suite
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

     
