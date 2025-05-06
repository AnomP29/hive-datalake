from pyspark.sql import SparkSession

# Initialize Spark with Hive support
spark = SparkSession.builder \
    .appName("RegisterHiveTable") \
    .enableHiveSupport() \
    .getOrCreate()

# SQL: Create external table pointing to S3/MinIO
spark.sql("""
CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi_partitioned (
    VendorID BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance DOUBLE,
    RatecodeID INT,
    store_and_fwd_flag STRING,
    PULocationID INT,
    DOLocationID INT,
    payment_type INT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
STORED AS PARQUET
LOCATION 's3a://nyc-taxi/partitioned/yellow/trip-data/'
""")

# Repair to detect partitions
spark.sql("MSCK REPAIR TABLE nyc_taxi_partitioned")

# Optional: show some rows
df = spark.sql("SELECT * FROM nyc_taxi_partitioned LIMIT 10")
df.show(truncate=False)

spark.stop()
