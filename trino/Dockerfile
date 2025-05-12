FROM eclipse-temurin:21-jdk-jammy


USER root

# Install dependencies for Trino and debugging tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    dnsutils \
    netcat \
    bash \
    ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix missing 'python' command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set Trino version
ENV TRINO_VERSION=437

# Install OpenJDK 21 from Eclipse Temurin
# Download and install OpenJDK 21 from Eclipse Temurin
# RUN mkdir -p /opt/openjdk
# COPY /trino/etc/utils/OpenJDK21U-jdk_x64_alpine-linux_hotspot_21_35.tar.gz /tmp/openjdk21.tar.gz
# RUN tar -xzvf /tmp/openjdk21.tar.gz -C /opt/openjdk && \
#     rm /tmp/openjdk21.tar.gz

# RUN curl -L https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21%2B35/OpenJDK21U-jdk_x64_alpine-linux_hotspot_21_35.tar.gz -o /tmp/openjdk21.tar.gz && \
#     mkdir -p /opt/openjdk && \
#     tar -xzf /tmp/openjdk21.tar.gz -C /opt/openjdk && \
#     rm /tmp/openjdk21.tar.gz

# Debug step: List files in /opt/openjdk to confirm OpenJDK was extracted
# RUN ls -l /opt/openjdk

# Add Trino to PATH
ENV PATH="/opt/trino/bin:${PATH}"

# Set JAVA_HOME and add bin to PATH
# ENV JAVA_HOME=/opt/openjdk/jdk-21
# ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Debug step: Verify Java installation
RUN java -version

COPY /trino/etc/utils/trino-server-437.tar.gz trino.tar.gz
RUN tar -xzvf trino.tar.gz && \
    mv trino-server-${TRINO_VERSION} /opt/trino && \
    rm trino.tar.gz

WORKDIR /opt/trino

COPY /trino/etc /opt/trino/etc

# Ensure plugin directories exist before copying jar files
RUN mkdir -p /usr/lib/trino/plugin/hive

# Copy your configurations
COPY /trino/etc/catalog/hive.properties /etc/trino/catalog/hive.properties
COPY /utils/lib/hadoop-aws-3.2.0.jar /usr/lib/trino/plugin/hive/
COPY /utils/lib/aws-java-sdk-bundle-1.11.901.jar /usr/lib/trino/plugin/hive/

# Expose Trino's default web UI port
EXPOSE 8080

# ENTRYPOINT ["/opt/trino/bin/trino"]

# Default command to run Trino
CMD ["bin/launcher", "run"]
