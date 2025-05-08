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
s3a_path = "s3a://nyc-taxi/raw/yellow_tripdata_*.parquet"

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
    # df_partitioned.printSchema()
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

table_schema = spark.table("nyc_taxi_trip").schema
ordered_columns = [f.name for f in table_schema if f.name in df_partitioned.columns]
df_ordered = df_partitioned.select(*ordered_columns)

# print(table_schema)
# df_ordered.printSchema()

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS nyc_taxi_trip (
    {columns_ddl}
)
PARTITIONED BY (
    pickup_date DATE
)
STORED AS PARQUET
"""
# df_partitioned.select("pickup_date").show(truncate=False)

# try:
#     # print(create_table_sql)
#     print('Creating Tables')
#     spark.sql(create_table_sql)
# except Exception as e:
#     print(e)

# Before writing Parquet
# spark.conf.set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")


# SQL: Create external table pointing to S3/MinIO
# spark.sql("""
# CREATE TABLE IF NOT EXISTS nyc_taxi_trip (
#     VendorID bigint,
#     tpep_pickup_datetime TIMESTAMP,
#     tpep_dropoff_datetime TIMESTAMP,
#     passenger_count INT,
#     trip_distance DOUBLE,
#     RatecodeID INT,
#     store_and_fwd_flag STRING,
#     PULocationID INT,
#     DOLocationID INT,
#     payment_type INT,
#     fare_amount DOUBLE,
#     extra DOUBLE,
#     mta_tax DOUBLE,
#     tip_amount DOUBLE,
#     tolls_amount DOUBLE,
#     improvement_surcharge DOUBLE,
#     total_amount DOUBLE,
#     congestion_surcharge DOUBLE,
#     airport_fee DOUBLE,
#     pickup_date date, 
#     year date, 
#     month date, 
#     day date
# )
# PARTITIONED BY (
#     pickup_date date
# )
# STORED AS PARQUET
# -- LOCATION 's3a://nyc-taxi/partitioned/yellow/trip-data/'
# """)
# Insert data into Hive table
# df_partitioned.select("pickup_date").show(10, truncate=False)

# try:
#     print("Writing data into Hive table...")
#     df_ordered.write.mode("overwrite").insertInto("nyc_taxi_trip")
# except Exception as e:
#     print(f"Error inserting data: {e}")

# Optional: Query to verify
try:
    print("Previewing data:")
    count_sql = '''
    SELECT pickup_date, count(1) pickup_count 
    FROM nyc_taxi_trip 
    GROUP BY 1 
    ORDER BY pickup_date
    '''
    spark.sql(count_sql).show(truncate=False)
except Exception as e:
    print(f"Error querying table: {e}")
    
# Repair to detect partitions
# spark.sql("MSCK REPAIR TABLE nyc_taxi_partitioned")

# Optional: show some rows
# spsql = """
#  SELECT * FROM nyc_taxi_partitioned LIMIT 10";
#  -- DESCRIBE nyc_taxi_trip;
# """
# df = spark.sql(spsql)
# df.show(truncate=False)

spark.stop()
