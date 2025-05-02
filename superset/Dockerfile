FROM apache/superset

ENV SUPERSET_SECRET_KEY=mysecret
USER root
RUN pip install --no-cache-dir trino sqlalchemy-trino
USER superset