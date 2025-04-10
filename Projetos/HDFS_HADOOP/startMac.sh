#!/bin/bash
# Desativa a exibição dos comandos (opcional)
# set +x

echo "Clonando repositório do GitHub..."

# Altere essa URL para o repositório que você quer clonar
git clone https://github.com/mjstealey/hadoop.git
# Em vez de "timeout /t 10" no Windows, usamos "sleep" para esperar 10 segundos
sleep 10
echo "Repositório clonado!"

echo "Iniciando Hadoop"
cd hadoop || { echo "Falha ao entrar no diretório hadoop"; exit 1; }
docker-compose up
docker-compose ps

echo "Hadoop Iniciado"

echo "Copiando CVS para a pasta /tmp/csvs"
# Ajuste o caminho de origem conforme sua estrutura de diretórios no macOS
docker cp /Users/joaobatistaromao/Desktop/TrabalhoBigData/Projeto-bigData/Projetos/web_Scraping/cvs a5cf31cb490d:/tmp/csvs

echo "Criando a pasta /tmp/code"
docker exec a5cf31cb490d mkdir -p /tmp/code

echo "Copiando Mapper para /tmp/code"
# Ajuste o caminho conforme necessário
docker cp /Users/joaobatistaromao/Desktop/TrabalhoBigData/Projeto-bigData/Projetos/HDFS_HADOOP/mapper.py a5cf31cb490d:/tmp/code/

echo "Copiando Reducer para /tmp/code"
docker cp /Users/joaobatistaromao/Desktop/TrabalhoBigData/Projeto-bigData/Projetos/HDFS_HADOOP/reducer.py a5cf31cb490d:/tmp/code/

echo "Iniciando Mapper-Reducer"
# Para iniciar uma sessão interativa, pode ser necessário usar -it;
# se o objetivo for executar comandos automaticamente, remova a parte interativa.
docker exec -it a5cf31cb490d bash -c 'export HADOOP_USER_NAME=hadoop; bash'

echo "Copiando cvs para o HDFS"
hdfs dfs -mkdir -p /dados/csv
hdfs dfs -put /tmp/csvs/*.csv /dados/csv

echo "Verificando se os dados foram copiados"
hdfs dfs -ls /dados/csv

echo "Iniciando Mapper e Reducer"

hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.9.0.jar \
  -file /tmp/code/mapper.py \
  -file /tmp/code/reducer.py \
  -input /dados/csv \
  -output /resultado/preco_medio_10 \
  -mapper "python mapper.py" \
  -reducer "python reducer.py"

# Exibe as primeiras 10 linhas do arquivo e passa para o mapper.py utilizando python (ajuste o caminho conforme necessário)
head -n 10 /Users/jbati/Documents/GitHub/Projeto-bigData/Projetos/web_Scraping/cvs/1o_Sem_2020__Combustiveis_Automotivos.csv | python mapper.py

# Equivalente ao Get-Content do PowerShell: usa head para obter as primeiras 50 linhas e passa para python2
head -n 50 /Users/jbati/Documents/GitHub/Projeto-bigData/Projetos/web_Scraping/cvs/1o_Sem_2020__Combustiveis_Automotivos.csv | python2 mapper.py

hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.9.0.jar -file /tmp/code/mapper.py -file /tmp/code/reducer.py -input /dados/teste/csv -output /resultado/preco_medio_TEST -mapper "python mapper.py" -reducer "python reducer.py"
