#!/bin/bash

set -e

export HIVE_METASTORE_JAVA_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=8000"

# Set the password environment variable
export PGPASSWORD="$HIVE_DB_PASSWORD"

# Wait for PostgreSQL to be ready
until pg_isready -h $HIVE_DB_HOST -p $HIVE_DB_PORT -U $HIVE_DB_USER; do
  echo "Waiting for PostgreSQL at $HIVE_DB_HOST:$HIVE_DB_PORT..."
  sleep 2
done

echo "PostgreSQL is ready"

# /opt/hive/bin/hiveserver2 &
# exec "$@"

echo "Starting Hive hive-Server2..."
exec /opt/hive/bin/hive --service hiveserver2
