from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as _sum, when, to_date

def main():
    # Inicializa a sessão do Spark com suporte ao Hive
    spark = SparkSession.builder \
        .appName("Ecommerce Batch ETL") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()

    # Ler dados brutos do HDFS (gravados pelo Flume)
    # Supondo que os dados estão em formato JSON
    raw_df = spark.read.json("hdfs://namenode:9000/ecommerce/raw/*/*")

    # ETL Básico: Adicionar coluna de data
    df = raw_df.withColumn("date", to_date(col("timestamp")))

    # Wide Dependency 1: Agregação por produto e data
    # (Total de cliques, Total de compras, Receita total)
    daily_stats = df.groupBy("date", "product_id").agg(
        count(when(col("event_type") == "view_item", True)).alias("total_views"),
        count(when(col("event_type") == "purchase", True)).alias("total_purchases"),
        _sum(when(col("event_type") == "purchase", col("price")).otherwise(0)).alias("revenue")
    )

    # Wide Dependency 2: Join com a tabela de produtos para pegar o nome
    # No mundo real, a dimensão de produtos estaria em outra tabela Hive
    # Para o exemplo, vamos apenas salvar a agregação diretamente

    # Criar tabela no Hive e inserir dados
    spark.sql("CREATE DATABASE IF NOT EXISTS ecommerce_dw")
    
    # Escrever no Hive
    daily_stats.write \
        .mode("append") \
        .partitionBy("date") \
        .saveAsTable("ecommerce_dw.daily_product_stats")

    print("ETL concluído com sucesso e dados gravados no Hive.")
    spark.stop()

if __name__ == "__main__":
    main()
