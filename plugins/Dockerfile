FROM --platform=linux/amd64 apache/airflow:2.10.5

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir apache-airflow-providers-common-sql==1.26.0 \
                               airflow-provider-great-expectations==0.3.0 \
                               -r requirements.txt