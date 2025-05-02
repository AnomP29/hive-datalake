FROM apache/hive:3.1.3

# Set environment variables for Hive and Hadoop
ENV HIVE_HOME=/opt/hive
ENV HADOOP_HOME=/opt/hadoop

# Run necessary initialization commands (fix permissions on HDFS)
RUN mkdir -p /tmp/hive && \
    chmod 1777 /tmp/hive && \
    chown hive:hive /tmp/hive

# Expose necessary ports
EXPOSE 9083 10000

# Switch to root to install packages
USER root

# Install postgresql-client and clean up
RUN apt-get update && apt-get install -y procps && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    # Remove unnecessary SLF4J bindings (log4j-slf4j-impl)
    rm -f /opt/hive/lib/log4j-slf4j-impl-*.jar && \
    rm -f /opt/hive/lib/slf4j-log4j12-*.jar && \
    rm -f /opt/hive/lib/slf4j-api-*.jar && \
    rm -f /opt/hive/lib/slf4j-jdk14-*.jar

# Ensure correct ownership of the Hive home directory
RUN mkdir -p /home/hive/.beeline && \
    chown -R hive:hive /home/hive

ADD https://jdbc.postgresql.org/download/postgresql-42.7.3.jar /opt/hive/lib/


# Change permissions to allow hive user to write to hive-site.xml
RUN chmod -R 777 /opt/hive/conf

COPY entrypoint.sh /entrypoint.sh
COPY hive-site.xml /opt/hive/conf/hive-site.xml
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Optionally switch back to hive user
# USER hive


# CMD ["--service", "metastore"]
