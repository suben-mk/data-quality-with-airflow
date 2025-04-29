# Data Quality with Airflow
โปรเจคนี้ผู้เขียนต้องการตรวจสอบคุณภาพของข้อมูล (Data Quality) ด้วยเครื่องมือ Great Expectations และ Common SQL Provider ใน Airflow ซึ่งจะใช้ข้อมูลจาก SQLite database มาทำการตรวจสอบคุณภาพของข้อมูลตามเงื่อนไขที่ผูเขียนกำหนด จะทำการตรวจสอบคุณภาพของข้อมูลในระดับตาราง (Table Level) และระดับคอลัมน์ (Column Level) ตามรายระเอียดข้างล่าง

### Specification
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
**destination** : audible_data_for_analytic.db

**Table Level Check**
table | expectation | success / fial |
----- | ----------- | -------------- |
audible_analytic | has column name to be in list | ✅ |
audible_analytic | has row count between min 1 and max 2000000 | ✅ |

**Column Level Check**
column	| expectation | success / fial |
------- | ----------- | -------------- |
timestamp | has not null values | ✅ |
user_id | has 8 characters values | ✅ |
country | has not null valuse | ✅ |
book_id | has integer type or number 0-9 | ✅ |
book_title | has not null values | ✅ |
categories | has valuse to be in list | ✅ |
categories | has not null values | ❌ |
THBprice | has valuse between min 20 and max 3000 | ❌ |
