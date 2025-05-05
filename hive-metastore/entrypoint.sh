#!/bin/bash

set -e

# Set the password environment variable
export PGPASSWORD="$HIVE_DB_PASSWORD"

# Wait for PostgreSQL to be ready
until pg_isready -h $HIVE_DB_HOST -p $HIVE_DB_PORT -U $HIVE_DB_USER; do
  echo "Waiting for PostgreSQL at $HIVE_DB_HOST:$HIVE_DB_PORT..."
  sleep 2
done

echo "PostgreSQL is ready"

# Check if the database exists
echo "Checking Database $HIVE_DB_NAME is Exists..."
if ! psql -h "$HIVE_DB_HOST" -U "$HIVE_DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$HIVE_DB_NAME"; then
  echo "Database $HIVE_DB_NAME does not exist. Creating..."
  psql -h "$HIVE_DB_HOST" -U "$HIVE_DB_USER" -c "CREATE DATABASE $HIVE_DB_NAME;"
else
  echo "Database $HIVE_DB_NAME already exists."
fi

# Try checking the schema
if /opt/hive/bin/schematool -dbType postgres -info; then
  echo "Hive Metastore schema already initialized."
else
  echo "Schema not found. Initializing Hive Metastore schema..."
  /opt/hive/bin/schematool -dbType postgres -initSchema
fi

echo "Starting Hive Metastore..."
exec /opt/hive/bin/hive --service metastore
