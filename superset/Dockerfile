FROM apache/superset

USER root

# Install PostgreSQL client, Trino, and related dependencies
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir trino sqlalchemy-trino && \
    pip install flask-limiter[redis] && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the init script and make it executable
COPY init-superset-db.sh /init-superset-db.sh
# COPY superset_config.py /superset_config.py
RUN chmod +x /init-superset-db.sh

# Default entrypoint to initialize the Superset DB
ENTRYPOINT ["/init-superset-db.sh"]

# Switch back to the superset user for security reasons
USER superset
