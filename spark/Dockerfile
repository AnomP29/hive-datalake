FROM bitnami/spark:3.5.0

USER root

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    libsnappy-dev \
    liblzo2-dev \
    liblz4-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Python packages
RUN pip3 install --no-cache-dir boto3 pyspark

# Download Hive & Hadoop dependencies
RUN mkdir -p /opt/bitnami/spark/jars /opt/bitnami/hive/lib && \
    curl -L -o /opt/bitnami/spark/jars/hive-metastore-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-metastore/3.1.3/hive-metastore-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-exec-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-exec/3.1.3/hive-exec-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-common-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-common/3.1.3/hive-common-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-serde-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-serde/3.1.3/hive-serde-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-jdbc-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3.jar && \
    curl -L -o /opt/bitnami/spark/jars/hive-runtime-3.1.3.jar https://repo1.maven.org/maven2/org/apache/hive/hive-runtime/3.1.3/hive-runtime-3.1.3.jar && \
    curl -L -o /opt/bitnami/hive/lib/hadoop-aws-3.2.0.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar && \
    curl -L -o /opt/bitnami/hive/lib/aws-java-sdk-bundle-1.11.901.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar

# Environment variables
ENV SPARK_HOME=/opt/bitnami/spark
ENV HADOOP_HOME=/opt/bitnami/spark
ENV HIVE_HOME=/opt/bitnami/hive/lib

WORKDIR /app
COPY ./conf/spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf

USER 1001
