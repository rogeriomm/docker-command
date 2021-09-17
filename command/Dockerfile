FROM rogermm/spark-base-python:3.1.2-hadoop3.2-java11-bdb

MAINTAINER Rogerio Matte Machado <rogermm@gmail.com>

ENV TZ=America/Sao_Paulo

ARG DEBIAN_FRONTEND=noninteractive

#RUN apt-get update && apt-get upgrade -y
RUN apt-get update

RUN apt-get install -y \
      openjdk-11-jdk \
      net-tools \
      curl \
      netcat \
      gnupg \
      wget \
      vim \
      links \
      bind9-dnsutils \
      inetutils-ping \
      git \
      htop \
      apt-file \
      net-tools \
      procps \
      htop \
      unzip \
      ack \
      tree \
      man-db \
      libpq-dev \
      librdkafka-dev

RUN apt-get upgrade -y

WORKDIR /root

RUN git clone https://github.com/apache/spark.git

RUN cd spark ; git checkout v3.1.2

RUN cd spark ; ./build/mvn -v

# Apache Maven: Setting up Maven’s Memory Usage
ENV MAVEN_OPTS="-Xmx2g -XX:ReservedCodeCacheSize=2g"

#RUN cd spark ; ./build/mvn -Pyarn -Phive -Phive-thriftserver -Dhadoop.version=3.3.1 -DskipTests --log-file build.txt clean package

# -Dhadoop.version=3.3.1
RUN cd spark ; \
    ./dev/make-distribution.sh --name custom-spark --pip --tgz \
         -Psparkr -Phive -Phive-thriftserver -Pyarn -Pkubernetes -Dhadoop.version=3.3.1

RUN cd spark ; \
    ./build/mvn --log-file build-package-log.txt -DskipTests package

RUN apt-get update ; apt-get upgrade -y ; apt clean

RUN apt-get install -y \
            tree

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

#ENTRYPOINT ["/entrypoint.sh"]
#CMD ["/bin/bash", "-c", "sleep 10000"]

#
# https://docs.delta.io/latest/releases.html: DELTA Lake Compatibility with Apache Spark
#
