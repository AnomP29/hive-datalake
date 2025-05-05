#!/bin/bash
# init-superset-db.sh

export SS_DB_HOST=172.27.16.1
export SS_DB_PORT=5432
export SS_DB_NAME=superset
export SS_DB_USER=postgres
export SS_DB_PASSWORD=postgres    
# export SQLALCHEMY_DATABASE_URI="postgresql://$SS_DB_USER:$SS_DB_PASSWORD@$SS_DB_HOST:$SS_DB_PORT/$SS_DB_NAME"

set -e

# Set the password environment variable
export PGPASSWORD="$SS_DB_PASSWORD"

# Wait for PostgreSQL to be ready
until pg_isready -h "$SS_DB_HOST" -p "$SS_DB_PORT"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "🔎 DATABASE_URL: $SQLALCHEMY_DATABASE_URI"

echo "🛠️ Checking if Superset DB '$SS_DB_NAME' exists..."
DB_EXIST=$(psql -h "$SS_DB_HOST" -U "$SS_DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$SS_DB_NAME'")
if [ "$DB_EXIST" != "1" ]; then
  echo "📦 Creating database $SS_DB_NAME..."
  createdb -h "$SS_DB_HOST" -U "$SS_DB_USER" "$SS_DB_NAME"
else
  echo "✅ Database $SS_DB_NAME already exists."
fi

# Run Superset initialization
echo "🚀 Initializing Superset..."
echo "🔧 Running DB migrations..."
superset db upgrade

# Check if tables were created after migration
# echo "🔍 Checking if tables were created..."
# TABLES=$(psql -h "$SS_DB_HOST" -U "$SS_DB_USER" -d "$SS_DB_NAME" -c "\dt" | grep -c "superset")
# if [ "$TABLES" -eq 0 ]; then
#   echo "❌ No Superset tables found in the database."
#   exit 1
# else
#   echo "✅ Superset tables created successfully."
# fi

echo "👤 Creating admin user (if not exists)..."
superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com \
  --password admin

# Initialize Superset
superset init

# Run Superset
echo "🚀 Running Superset on 0.0.0.0:8088"
superset run -h 0.0.0.0 -p 8088
