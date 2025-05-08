from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType


# Create Spark session with MinIO config
spark = SparkSession.builder \
    .appName("ReadFromMinIO") \
    .enableHiveSupport() \
    .getOrCreate()

# Path to the Parquet file/folder in MinIO
s3a_path = "s3a://nyc-taxi/raw/yellow_tripdata_*.parquet"

# Read Parquet file
df = spark.read.parquet(s3a_path)

# Ensure datetime column exists
pickup_col = "tpep_pickup_datetime" if "tpep_pickup_datetime" in df.columns else df.columns[0]

# Before writing Parquet
spark.conf.set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")

# Add partition columns (year, month, day)
df_partitioned = df.withColumn("pickup_date", to_date(col(pickup_col))) \
    .withColumn("year", col("pickup_date").substr(1, 4)) \
    .withColumn("month", col("pickup_date").substr(6, 2)) \
    .withColumn("day", col("pickup_date").substr(9, 2))

# Show result
# df_partitioned.show()

# Write partitioned Parquet to MinIO
output_path = "s3a://nyc-taxi/partitioned/yellow/trip-data/"

df_clean = df_partitioned.withColumn("VendorID", col("VendorID").cast("long")) \
             .withColumn("passenger_count", col("passenger_count").cast(IntegerType())) \
             .withColumn("RatecodeID", col("RatecodeID").cast(IntegerType())) \
             .withColumn("PULocationID", col("PULocationID").cast(IntegerType())) \
             .withColumn("DOLocationID", col("DOLocationID").cast(IntegerType())) \
             .withColumn("payment_type", col("payment_type").cast(IntegerType())) 

df_clean.write \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .parquet(output_path)

# # Write partitioned Parquet to Hive Table
# df_clean.write \
#     .mode("overwrite") \
#     .format("parquet") \
#     .partitionBy("year", "month", "day") \
#     .saveAsTable("nyc_taxi_partitioned")

print("✔️ Data written successfully with partitions: year, month, day.")