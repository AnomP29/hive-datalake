FROM apache/hive:3.1.3

# Set environment variables for Hive and Hadoop
ENV HIVE_HOME=/opt/hive
ENV HADOOP_HOME=/opt/hadoop

# Run necessary initialization commands (fix permissions on HDFS)
RUN mkdir -p /tmp/hive && \
    chmod 1777 /tmp/hive && \
    chown hive:hive /tmp/hive

# Expose necessary ports
EXPOSE 9083

# Switch to root to install packages
USER root

# Install postgresql-client and clean up
RUN apt-get update && apt-get install -y procps && \
    apt-get install -y curl postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    # Remove unnecessary SLF4J bindings (log4j-slf4j-impl)
    rm -f /opt/hive/lib/log4j-slf4j-impl-*.jar && \
    rm -f /opt/hive/lib/slf4j-log4j12-*.jar && \
    rm -f /opt/hive/lib/slf4j-api-*.jar && \
    rm -f /opt/hive/lib/slf4j-jdk14-*.jar 

# Ensure correct ownership of the Hive home directory
RUN mkdir -p /home/hive/.beeline && \
    chown -R hive:hive /home/hive

# Add necessary libraries (PostgreSQL, Hadoop, and AWS SDK)
ADD https://jdbc.postgresql.org/download/postgresql-42.7.3.jar /opt/hive/lib/

# Download Hadoop (with third-party dependencies) and extract
# RUN curl -O https://archive.apache.org/dist/hadoop/common/hadoop-3.3.1/hadoop-3.3.1.tar.gz && \
#     tar -xzvf hadoop-3.3.1.tar.gz -C /opt/hadoop
# RUN tar -xzvf /utils/lib/hadoop-3.3.1.tar.gz -C /opt/hadoop
COPY /utils/lib/hadoop-3.3.1.tar.gz /utils/lib/hadoop-3.3.1.tar.gz
RUN tar -xzvf /utils/lib/hadoop-3.3.1.tar.gz -C /opt/hadoop

COPY utils/lib/hadoop-aws-3.2.0.jar /opt/hive/lib/hadoop-aws-3.2.0.jar
COPY utils/lib/aws-java-sdk-bundle-1.11.901.jar /opt/hive/lib/aws-java-sdk-bundle-1.11.901.jar
# RUN curl -L -o /opt/hive/lib/hadoop-aws-3.2.0.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar && \
#     curl -L -o /opt/hive/lib/aws-java-sdk-bundle-1.11.901.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar

# Add Hadoop JARs (hadoop-common, hadoop-aws, etc.)
# ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.1/hadoop-common-3.3.1.jar /opt/hive/lib/
# ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/3.3.1/hadoop-auth-3.3.1.jar /opt/hive/lib/
# ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar /opt/hive/lib/
# ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar /opt/hive/lib/

# Add Hadoop Thirdparty JAR (to resolve ThreadFactoryBuilder issue)
# ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-thirdparty/3.3.1/hadoop-thirdparty-3.3.1.jar /opt/hive/lib/

# Add Guava 19.0 (Hadoop 3.3.x Compatibility)
ADD https://repo1.maven.org/maven2/com/google/guava/guava/19.0/guava-19.0.jar /opt/hive/lib/



# Change permissions to allow hive user to write to hive-site.xml
RUN chmod -R 777 /opt/hive/conf

COPY hive-metastore/entrypoint.sh /entrypoint.sh
COPY config/hive-site.xml /opt/hive/conf/hive-site.xml
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Optionally switch back to hive user
# USER hive


# CMD ["--service", "metastore"]
