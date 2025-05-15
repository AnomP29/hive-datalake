FROM openjdk:8-jdk-slim

ENV HIVE_VERSION=3.1.3 \
    HADOOP_VERSION=3.3.1 \
    HIVE_HOME=/opt/hive \
    HADOOP_HOME=/opt/hadoop \
    PATH="/opt/hive/bin:$PATH"

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    postgresql-client \
    procps \
    netcat \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Download and install Hive
RUN curl -fsSL https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz | \
    tar -xz -C /opt && mv /opt/apache-hive-${HIVE_VERSION}-bin ${HIVE_HOME}

# Download and install Hadoop minimal set
RUN curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz | \
    tar -xz -C /opt && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm -rf ${HADOOP_HOME}/share/doc \
           ${HADOOP_HOME}/share/hadoop/tools/lib/*  \
           ${HADOOP_HOME}/share/hadoop/mapreduce/*examples* \
           ${HADOOP_HOME}/share/hadoop/yarn/*test* \
           ${HADOOP_HOME}/share/hadoop/hdfs/*test*

# Add AWS S3 support jars
RUN curl -fsSL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar -o ${HIVE_HOME}/lib/hadoop-aws.jar && \
    curl -fsSL https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar -o ${HIVE_HOME}/lib/aws-java-sdk-bundle.jar && \
    curl -fsSL https://repo1.maven.org/maven2/com/google/guava/guava/19.0/guava-19.0.jar -o ${HIVE_HOME}/lib/guava-19.0.jar


RUN rm -f /opt/hive/lib/log4j-slf4j-impl-*.jar \
    && rm -f /opt/hive/lib/slf4j-log4j12-*.jar \
    && rm -f /opt/hive/lib/slf4j-api-*.jar \
    && rm -f /opt/hive/lib/slf4j-jdk14-*.jar \
    && rm -f /opt/hive/lib/log4j-1.2*.jar

# Add required Log4j 2 libraries
RUN curl -L -o /opt/hive/lib/log4j-api-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.17.1/log4j-api-2.17.1.jar && \
    curl -L -o /opt/hive/lib/log4j-core-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.17.1/log4j-core-2.17.1.jar && \
    curl -L -o /opt/hive/lib/log4j-slf4j-impl-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-slf4j-impl/2.17.1/log4j-slf4j-impl-2.17.1.jar

# Add PostgreSQL JDBC
RUN curl -fsSL https://jdbc.postgresql.org/download/postgresql-42.7.3.jar -o ${HIVE_HOME}/lib/postgresql-42.7.3.jar

# Add AWS credentials for MinIO
RUN mkdir -p ${HIVE_HOME}/.aws && \
    echo "[default]" > ${HIVE_HOME}/.aws/credentials && \
    echo "aws_access_key_id = minioadmin" >> ${HIVE_HOME}/.aws/credentials && \
    echo "aws_secret_access_key = minioadmin" >> ${HIVE_HOME}/.aws/credentials && \
    echo "[default]" > ${HIVE_HOME}/.aws/config && \
    echo "region = asia-sea-1" >> ${HIVE_HOME}/.aws/config && \
    echo "output = json" >> ${HIVE_HOME}/.aws/config

# Add hive-site.xml and entrypoint
COPY config/hive-site.xml ${HIVE_HOME}/conf/hive-site.xml
COPY hive-metastore/conf/log4j2.properties ${HIVE_HOME}/conf/hive-log4j2.properties
COPY hive-metastore/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && chmod 644 ${HIVE_HOME}/conf/*.xml ${HIVE_HOME}/conf/*.properties

# Ports: Hive Metastore (9083), HiveServer2 (10000)
EXPOSE 9083 10000

ENTRYPOINT ["/entrypoint.sh"]
