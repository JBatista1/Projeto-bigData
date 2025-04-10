from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, stddev, expr, percentile_approx, max, rank, regexp_replace
from pyspark.sql.window import Window
from io import StringIO
from contextlib import redirect_stdout

# Criando SparkSession
spark = SparkSession.builder.appName("Analise de Combustíveis").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Lendo todos os arquivos CSV da pasta
df = spark.read.csv("/Users/joaobatistaromao/Desktop/TrabalhoBigData/Projeto-bigData/Projetos/web_Scraping/cvs/", header=True, inferSchema=True, sep=";")

# Limpando e convertendo a coluna "Valor de Venda"
df = df.withColumn("Valor de Venda", regexp_replace("Valor de Venda", "R\\$|\\s", ""))
df = df.withColumn("Valor de Venda", regexp_replace("Valor de Venda", ",", "."))
df = df.withColumn("Valor de Venda", col("Valor de Venda").cast("double"))

# Filtrando os combustíveis de interesse
combustiveis = ["GASOLINA", "ETANOL", "DIESEL", "DIESEL S10"]
df_filtrado = df.filter(col("Produto").isin(combustiveis))

# --- Estatísticas gerais: média, mediana e desvio padrão ---
estatisticas = df_filtrado.groupBy("Produto").agg(
    mean("Valor de Venda").alias("media"),
    percentile_approx("Valor de Venda", 0.5).alias("mediana"),
    stddev("Valor de Venda").alias("desvio_padrao")
)

print("📊 Estatísticas por combustível")
estatisticas.show()

# Filtrar SP e os combustíveis desejados
df_sp = df_filtrado.filter(
    (col("Estado - Sigla") == "SP") &
    (col("Produto").isin(["GASOLINA", "ETANOL", "DIESEL"]))
)

# Calcular média por revenda
postos_media = df_sp.groupBy("Revenda") \
    .agg(mean("Valor de Venda").alias("media")) \
    .orderBy(col("media").desc()) \
    .limit(3)

print("🌎 3 principais postos de São Paulo que têm a maior média de venda da gasolina, etanol e Diesel")
postos_media.show(truncate=False)

# --- Estado com maior média de venda de DIESEL e DIESEL S10 ---
diesel_estados = df_filtrado.filter(col("Produto").isin(["DIESEL", "DIESEL S10"])) \
    .groupBy("Estado - Sigla", "Produto") \
    .agg(mean("Valor de Venda").alias("media")) \
    .orderBy(col("media").desc()) \
    .limit(1)

print("🌎 Estado com maior média de DIESEL e DIESEL S10")
diesel_estados.show()

# --- Maior valor por bandeira no estado de SP ---
bandeiras_sp = df_sp.groupBy("Bandeira") \
    .agg(max("Valor de Venda").alias("max_valor")) \
    .orderBy(col("max_valor").desc())

print("🚩 Maior valor de venda por bandeira em SP")
bandeiras_sp.show()

# --- Município com maior e menor preço médio do DIESEL ---
diesel_df = df_filtrado.filter(
    (col("Produto") == "DIESEL") & col("Valor de Venda").isNotNull()
)

municipios_diesel = diesel_df.groupBy("Municipio") \
    .agg(mean("Valor de Venda").alias("media"))

maior = municipios_diesel.orderBy(col("media").desc()).limit(1)
menor = municipios_diesel.orderBy(col("media").asc()).limit(1)

print("📍 Município com maior preço médio do DIESEL:")
maior.show()

print("📍 Município com menor preço médio do DIESEL:")
menor.show()

# --- Top 3 bairros de Recife com maior média para DIESEL e DIESEL S10 ---
recife_bairros = df_filtrado.filter(
    (col("Municipio") == "RECIFE") & col("Produto").isin(["DIESEL", "DIESEL S10"])
).groupBy("Bairro", "Produto") \
 .agg(mean("Valor de Venda").alias("media")) \
 .orderBy(col("media").desc()) \
 .limit(3)

print("🏘️ Top 3 bairros de Recife com maior média de DIESEL e DIESEL S10:")
recife_bairros.show(10)
