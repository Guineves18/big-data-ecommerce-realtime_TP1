FROM python:3.9-slim

# Instalar Java (necessário para o Flume e Hadoop libs)
RUN apt-get update && apt-get install -y openjdk-11-jre-headless wget tar procps netcat

# Instalar Flume
ENV FLUME_VERSION=1.11.0
RUN wget -q https://dlcdn.apache.org/flume/${FLUME_VERSION}/apache-flume-${FLUME_VERSION}-bin.tar.gz && \
    tar -xzf apache-flume-${FLUME_VERSION}-bin.tar.gz -C /opt/ && \
    rm apache-flume-${FLUME_VERSION}-bin.tar.gz && \
    mv /opt/apache-flume-${FLUME_VERSION}-bin /opt/flume

ENV FLUME_HOME=/opt/flume
ENV PATH=$PATH:$FLUME_HOME/bin

WORKDIR /app

# Instalar bibliotecas Python para o gerador
COPY gerador/requirements.txt /app/gerador/requirements.txt
# (Se não houver requirements.txt ainda, ignoramos erros ou criamos depois)
RUN pip install --no-cache-dir -r /app/gerador/requirements.txt || echo "No requirements.txt found or failed to install"
