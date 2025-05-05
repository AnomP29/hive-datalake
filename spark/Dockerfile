# Start from the official Spark image
FROM bitnami/spark:latest


USER root

# Install Python and required dependencies
RUN mkdir -p /var/lib/apt/lists/partial \
    && apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    libsnappy-dev liblzo2-dev liblz4-dev && \
    apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PySpark (if not already included in the base image)
RUN pip3 install pyspark
RUN pip3 install boto3 pyspark

# Install the required Hive version (3.1.3)
RUN mkdir -p /opt/bitnami/spark/jars && \
    curl -L -o /opt/bitnami/spark/jars/hive-metastore-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-metastore/3.1.3/hive-metastore-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-exec-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-exec/3.1.3/hive-exec-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-common-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-common/3.1.3/hive-common-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-serde-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-serde/3.1.3/hive-serde-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-jdbc-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-runtime-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-runtime/3.1.3/hive-runtime-3.1.3.jar

# Set the Spark and Hadoop versions
ENV SPARK_HOME=/opt/bitnami/spark
ENV HADOOP_HOME=/opt/bitnami/spark
ENV HIVE_HOME=/opt/bitnami/spark
# Set the working directory inside the container
WORKDIR /app

# Copy the Spark Python script into the container
COPY ./python_script/spark-query.py /app/
# Copy the spark-defaults.conf file into the container
COPY ./conf/spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf

# Set the entrypoint to run the script
ENTRYPOINT ["python3", "/app/spark-query.py"]
