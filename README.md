# Build Datalake data from nyc_taxi_trip

## Technologies:

- **OS:** Windows11 using wsl2
- **Container:** docker-compose
- **Storage:** MinIO
- **Format:** Parquet
- **Table Format:** Apache Hive
- **Query Engine:** Apache Spark, Trino
- **Catalog:** Hive Metastore
- **BI Tool:** Apache Superset

## How To Deploy
- Create Docker Network
`docker network create datalake-net`
- Run `docker-compose up --build -d`
