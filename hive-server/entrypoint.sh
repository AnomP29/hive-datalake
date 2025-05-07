#!/bin/bash
set -e

export HIVE_METASTORE_JAVA_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=8000"

export PGPASSWORD="$HIVE_DB_PASSWORD"

# Wait for PostgreSQL to be ready
until pg_isready -h $HIVE_DB_HOST -p $HIVE_DB_PORT -U $HIVE_DB_USER; do
  echo "Waiting for PostgreSQL at $HIVE_DB_HOST:$HIVE_DB_PORT..."
  sleep 2
done

echo "PostgreSQL is ready"

# Ensure /tmp/hive exists in HDFS and is writable
hdfs dfs -mkdir -p /tmp/hive || true
hdfs dfs -chmod 1777 /tmp/hive || true

echo "....Starting HiveServer2..."
exec /opt/hive/bin/hiveserver2 --service hiveserver2
