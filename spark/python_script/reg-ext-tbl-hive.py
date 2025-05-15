from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, TimestampType, DateType

spark = SparkSession.builder \
    .appName("RegisterHiveTable") \
    .enableHiveSupport() \
    .getOrCreate()

spark.conf.set("hive.exec.dynamic.partition", "true")
spark.conf.set("hive.exec.dynamic.partition.mode", "nonstrict")

create_table_sql = f"""
CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi_trip_yellow (
    {columns_ddl}
)
PARTITIONED BY (
    pickup_date DATE
)
STORED AS PARQUET
LOCATION 's3a://nyc-taxi/yellow/trip-data/'
"""
spark.sql(create_table_sql)