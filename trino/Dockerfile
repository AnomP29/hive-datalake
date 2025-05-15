FROM trinodb/trino:437
# FROM eclipse-temurin:21-jdk-jammy

USER root

# Set Trino version
ENV TRINO_VERSION=437
WORKDIR /usr/lib/trino

# COPY /trino/etc/config.properties /usr/lib/trino/etc

# Ensure plugin directories exist before copying jar files
RUN mkdir -p /usr/lib/trino/plugin/hive

# Copy your configurations
COPY /trino/etc/ /usr/lib/trino/etc
COPY /trino/catalog/ /usr/lib/trino/etc/catalog
COPY /utils/lib/hadoop-aws-3.2.0.jar /usr/lib/trino/lib/
COPY /utils/lib/aws-java-sdk-bundle-1.11.901.jar /usr/lib/trino/lib/
COPY /trino/hadoop/ /usr/lib/trino/etc/catalog

# Expose Trino's default web UI port
EXPOSE 8080

# Default command to run Trino
CMD ["/usr/lib/trino/bin/launcher", "run"]
