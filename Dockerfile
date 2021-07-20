FROM ubuntu:focal

MAINTAINER Rogerio Matte Machado <rogermm@gmail.com>

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y \
      openjdk-11-jdk \
      net-tools \
      curl \
      netcat \
      gnupg \
      wget \
      vim \
      links \
      unzip

RUN apt-get install -y apt-file
RUN apt-file update

RUN apt-get install -y \
      python3 \
      ipython3

RUN apt-get install -y \
     net-tools \
     procps \
     htop \
     python3-pip \
     libpq-dev \
     librdkafka-dev

#postgresql-common
RUN pip3 install faker
RUN pip3 install pandas
RUN pip3 install psycopg2
RUN pip3 install elasticsearch
RUN pip3 install great_expectations
RUN pip3 install jupyter
RUN pip3 install confluent-kafka
RUN pip3 install findspark

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

#ENTRYPOINT ["/entrypoint.sh"]
#CMD ["/bin/bash", "-c", "sleep 10000"]
