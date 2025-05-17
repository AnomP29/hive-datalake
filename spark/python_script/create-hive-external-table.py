from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from py4j.java_gateway import java_import
from functools import reduce
import re


# Initialize Spark with Hive support
# spark = SparkSession.builder \
#     .appName("RegisterHiveTable") \
#     .enableHiveSupport() \
#     .getOrCreate()

builder = SparkSession.builder \
    .appName("MyApp") \
    .master("spark://spark:7077") \
    .enableHiveSupport()

# add this *before* .getOrCreate()
builder = builder \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.addressing.style", "path") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

spark = builder.getOrCreate()

spark.conf.set("hive.exec.dynamic.partition", "true")
spark.conf.set("hive.exec.dynamic.partition.mode", "nonstrict")

canonical_schema = StructType([
    StructField("VendorID", LongType()),
    StructField("tpep_pickup_datetime", TimestampType()),
    StructField("tpep_dropoff_datetime", TimestampType()),
    StructField("passenger_count", DoubleType()),
    StructField("trip_distance", DoubleType()),
    StructField("RatecodeID", DoubleType()),
    StructField("store_and_fwd_flag", StringType()),
    StructField("PULocationID", LongType()),
    StructField("DOLocationID", LongType()),
    StructField("payment_type", LongType()),
    StructField("fare_amount", DoubleType()),
    StructField("extra", DoubleType()),
    StructField("mta_tax", DoubleType()),
    StructField("tip_amount", DoubleType()),
    StructField("tolls_amount", DoubleType()),
    StructField("improvement_surcharge", DoubleType()),
    StructField("total_amount", DoubleType()),
    StructField("congestion_surcharge", DoubleType()),
    StructField("airport_fee", DoubleType(), nullable=True),
    StructField("cbd_congestion_fee", DoubleType(), nullable=True),
])

# Load all file paths using Spark
all_files_df = spark.read.format("binaryFile").load("s3a://nyc-taxi/raw/")

print('Get file bucket')
# Filter only Parquet files starting with yellow_tripdata_YYYY-MM.parquet
parquet_files = (
    all_files_df
    .filter(col("path").rlike(r"yellow_tripdata_\d{4}-\d{2}\.parquet$"))
    .select("path")
    .rdd.flatMap(lambda x: x)
    .collect()
)

# Read, Cast, and Union
dfs = []
for file_path in parquet_files:
    try:
        df_part = spark.read.parquet(file_path)
        for field in canonical_schema.fields:
            if field.name in df_part.columns:
                df_part = df_part.withColumn(field.name, col(field.name).cast(field.dataType))
            else:
                df_part = df_part.withColumn(field.name, lit(None).cast(field.dataType))
        dfs.append(df_part.select([f.name for f in canonical_schema.fields]))
    except Exception as e:
        print(f"Skipping {file_path}: {e}")

# Path to input parquet files on MinIO
# input_path = "s3a://nyc-taxi/raw/yellow_tripdata_*.parquet"

print('Read, Cast, and Union')
from functools import reduce

       
df = reduce(lambda a, b: a.unionByName(b), dfs)

# Path to output partitioned parquet folder on MinIO
output_path = "s3a://nyc-taxi/trip-data/yellow/"

# Determine pickup datetime column
pickup_col = "tpep_pickup_datetime" if "tpep_pickup_datetime" in df.columns else df.columns[0]

# Cast TimestampNTZ columns to Timestamp (if any)
for field in df.schema.fields:
    if "TimestampNTZType" in str(field.dataType):
        df = df.withColumn(field.name, col(field.name).cast(TimestampType()))

# Clean invalid dates and add pickup_date column as date
df_cleaned = df.withColumn("pickup_date", to_date(col(pickup_col)))

# Filter out rows with null pickup_date (optional)
df_cleaned = df_cleaned.filter(col("pickup_date").isNotNull())

# Add year/month/day columns (optional, for downstream usage)
df_partitioned = df_cleaned \
    .withColumn("year", year(col("pickup_date")).cast("string")) \
    .withColumn("month", format_string("%02d", month(col("pickup_date")))) \
    .withColumn("day", format_string("%02d", dayofmonth(col("pickup_date"))))

# Write partitioned parquet files to MinIO
# df_partitioned.write \
#     .mode("overwrite") \
#     .partitionBy("pickup_date") \
#     .parquet(output_path)

# Prepare table schema DDL excluding partition columns
partition_cols = {"pickup_date"}
base_columns = [f for f in df_partitioned.schema.fields if f.name not in partition_cols]
columns_ddl = ",\n    ".join([f"{f.name} {f.dataType.simpleString()}" for f in base_columns])

# Create external Hive table pointing to the written data
create_table_sql = f"""
CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi_trip_yellow (
    {columns_ddl}
)
PARTITIONED BY (
    pickup_date DATE
)
STORED AS PARQUET
LOCATION '{output_path}'
"""
# spark.sql(create_table_sql)

table_schema = spark.table("nyc_taxi_trip_yellow").schema
ordered_columns = [f.name for f in table_schema if f.name in df_partitioned.columns]
df_ordered = df_partitioned.select(*ordered_columns)
df_orderedf = df_ordered.withColumn("VendorID", col("VendorID").cast("bigint"))

# spark.sql("MSCK REPAIR TABLE nyc_taxi_trip_yellow")

# try:
#     print("Writing data into Hive table...")
#     df_ordered.write.mode("overwrite").insertInto("nyc_taxi_trip_yellow")
# except Exception as e:
#     print(f"Error inserting data: {e}")

spark.sql("SHOW TABLES").show()
# print("Creating Hive external table...")


# print("Repairing table to discover partitions...")
# spark.sql("MSCK REPAIR TABLE nyc_taxi_trip_yellow")

print("Listing partitions...")
spark.sql("SHOW PARTITIONS nyc_taxi_trip_yellow").show(truncate=False)

spark.stop()
