from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, TimestampType, DateType


# Initialize Spark with Hive support
spark = SparkSession.builder \
    .appName("RegisterHiveTable") \
    .enableHiveSupport() \
    .getOrCreate()

spark.conf.set("hive.exec.dynamic.partition", "true")
spark.conf.set("hive.exec.dynamic.partition.mode", "nonstrict")

# Path to the Parquet file/folder in MinIO
# s3a_path = "s3a://nyc-taxi/raw/yellow_tripdata_*.parquet"
s3a_path = "s3a://nyc-taxi/raw/green_tripdata_2021-01.parquet"

# Read Parquet file
df = spark.read.parquet(s3a_path)

# Ensure datetime column exists
pickup_col = "tpep_pickup_datetime" if "tpep_pickup_datetime" in df.columns else df.columns[0]

# Handle timestamp_ntz columns by casting them to timestamp (only if required)
for field in df.schema.fields:
    # print(field, str(field.dataType))
    if "TimestampNTZType" in str(field.dataType):  # Check for timestamp_ntz data type
        # print(field)
        df = df.withColumn(field.name, col(field.name).cast(TimestampType()))
        # print(field.name, DataType())
        # Print the column's data type after the cast inside the loop
        casted_col_type = df.schema[field.name].dataType
        # print(f"Inside Loop After Casting - Column {field.name} Data Type: {str(casted_col_type)}")

# df.printSchema()

try:
    # Clean invalid date rows by filtering them out
    df_cleaned = df.filter(to_date(col(pickup_col), "yyyy-MM-dd").isNotNull())

    # Or replace invalid date formats with null
    df_cleaned = df.withColumn("pickup_date", 
                            when(to_date(col(pickup_col), "yyyy-MM-dd").isNotNull(), 
                                    to_date(col(pickup_col), "yyyy-MM-dd"))
                            .otherwise(lit(None)))
    # Add partitioning columns
    df_partitioned = df_cleaned.withColumn("pickup_date", col("pickup_date").cast("date")) \
        .withColumn("year", year(col("pickup_date")).cast("string")) \
        .withColumn("month", format_string("%02d", month(col("pickup_date")))) \
        .withColumn("day", format_string("%02d", dayofmonth(col("pickup_date"))))

    df_partitioned.printSchema()
except Exception as e:
    print(e)

# Define base (non-partition) columns
base_columns = [f for f in df_partitioned.schema.fields if f.name not in {"pickup_date"}]
columns_ddl = ",\n    ".join([f"{f.name} {f.dataType.simpleString()}" for f in base_columns])
# print(base_columns)
# print(columns_ddl)
# Define partition column(s)
# partition_cols = ["pickup_date DATE"]
# df_partitioned.printSchema()


# print(table_schema)
# df_ordered.printSchema()

create_table_sql = f"""
CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi_trip_green (
    {columns_ddl}
)
PARTITIONED BY (
    pickup_date DATE
)
STORED AS PARQUET
LOCATION 's3a://nyc-taxi/green/trip-data/'
"""

try:
    # print(create_table_sql)
    print('Creating Tables')
    spark.sql(create_table_sql)
except Exception as e:
    print(e)

spark.sql('MSCK REPAIR TABLE nyc_taxi_trip_green;')
# table_schema = spark.table("nyc_taxi_trip").schema
# ordered_columns = [f.name for f in table_schema if f.name in df_partitioned.columns]
# df_ordered = df_partitioned.select(*ordered_columns)

spark.stop()