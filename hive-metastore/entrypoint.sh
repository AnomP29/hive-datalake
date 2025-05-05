#!/bin/bash

set -e
# Wait for PostgreSQL to be ready
until pg_isready -h $HIVE_DB_HOST -p $HIVE_DB_PORT -U $HIVE_DB_USER; do
  echo "Waiting for PostgreSQL at $HIVE_DB_HOST:$HIVE_DB_PORT..."
  sleep 2
done

echo "PostgreSQL is ready. Checking schema..."

# Try checking the schema
if /opt/hive/bin/schematool -dbType postgres -info; then
  echo "Hive Metastore schema already initialized."
else
  echo "Schema not found. Initializing Hive Metastore schema..."
  /opt/hive/bin/schematool -dbType postgres -initSchema
fi

echo "Starting Hive Metastore..."
exec /opt/hive/bin/hive --service metastore
