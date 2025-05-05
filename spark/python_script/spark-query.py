from pyspark.sql import SparkSession
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("Save to Hive on MinIO") \
    .enableHiveSupport() \
    .getOrCreate()

# Create DataFrame
data = [
    ("TX001", 15000.0, "2025-05-04"),
    ("TX002", 22000.0, "2025-05-05")
]
schema = StructType([
    StructField("id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("sale_date", StringType(), True)
])
df = spark.createDataFrame(data, schema)

# Save as Parquet to MinIO
df.write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", "s3a://datalake-example/sales_data/") \
    .saveAsTable("sales_data")  # Registered in Hive

df.show()
