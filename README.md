# Projeto de Big Data em Tempo Real - E-commerce

Este repositório contém a arquitetura completa do projeto prático de Big Data, abordando geração de dados, ingestão, streaming e processamento em lote.

## Requisitos
- Docker e Docker Compose instalados.
- Pelo menos 8GB a 12GB de RAM disponíveis.

## Estrutura
- `gerador/`: Script Python que simula eventos de e-commerce.
- `flume/`: Configuração do Apache Flume para ingerir logs.
- `streaming/`: Job do Apache Flink (Streaming e Alertas no HBase).
- `batch/`: Job do Apache Spark (ETL e consolidação no Hive).

## Como Executar

### 1. Subir a infraestrutura
```bash
docker-compose up -d
```
Aguarde alguns minutos para que todos os serviços (Hadoop, HBase, Hive, Flink, Spark) iniciem corretamente.

### 2. Acessar o contêiner de ingestão
```bash
docker exec -it ingestao bash
```

### 3. Iniciar o gerador de dados (dentro do contêiner)
```bash
python /app/gerador/gerador.py
```
Isso começará a escrever logs continuamente em `/app/gerador/ecommerce_events.log`.

### 4. Iniciar o Flume (em outro terminal dentro do contêiner)
```bash
flume-ng agent --conf-file /app/flume/flume.conf --name a1 -Dflume.root.logger=INFO,console
```
O Flume enviará os logs para o HDFS.

### 5. Executar o Job de Streaming (Flink)
Submeta o job ao cluster do Flink (que está rodando no contêiner `jobmanager`):
```bash
flink run -m jobmanager:8081 -py /app/streaming/flink_job.py
```

### 6. Executar o Job Batch (Spark)
Submeta o job ao Spark para consolidar os dados no final do dia (ou quando desejar):
```bash
spark-submit --master spark://spark-master:7077 /app/batch/spark_etl.py
```

## Validação (HDFS, Hive e HBase)
- **HDFS:** Para listar os dados brutos salvos pelo Flume: `hdfs dfs -ls /ecommerce/raw`
- **Hive:** Para consultar o Data Warehouse gerado pelo Spark, acesse o HiveServer e execute: `SELECT * FROM ecommerce_dw.daily_product_stats;`
