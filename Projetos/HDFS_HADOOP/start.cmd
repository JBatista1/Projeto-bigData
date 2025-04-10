@echo off
echo Clonando repositório do GitHub...

REM Altere essa URL para o repositório que você quer clonar
git clone https://github.com/mjstealey/hadoop.git
timeout /t 10
echo Repositório clonado!

echo Iniciando Hadoop
cd hadoop
docker-compose up
docker-compose ps

echo Hadoop Iniciado

echo Copiando CVS pasta tmp/csvs
docker cp \Users\jbati\Documents\GitHub\Projeto-bigData\Projetos\web_Scraping\cvs  9e78f6a31c81:/tmp/csvs

echo Criando pasta tmp/code
docker exec 9e78f6a31c81 mkdir -p /tmp/code

echo Copiando Mapper pasta tmp/code
docker cp :\Users\jbati\Documents\GitHub\Projeto-bigData\Projetos\HDFS_HADOOP\mapper.py 9e78f6a31c81:tmp/code/

echo Copiando Reducer pasta tmp/code
docker cp :\Users\jbati\Documents\GitHub\Projeto-bigData\Projetos\HDFS_HADOOP\reducer.py 9e78f6a31c81:tmp/code/

echo Iniciando Mapper-Reducer
docker exec -it 9e78f6a31c81 bash
export HADOOP_USER_NAME=hadoop

echo Copiando cvs para o hdfs
hdfs dfs -mkdir -p /dados/csv
hdfs dfs -put /tmp/csvs/*.csv /dados/csv

echo verificar se copiou os dados
hdfs dfs -ls /dados/csv

echo Iniciando Mapper e Reducer
hadoop jar hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.9.0.jar \
  -input /dados/csv \
  -output /resultado/preco_medio_sp \
  -mapper "python3 /tmp/code/mapper.py" \
  -reducer "python3 /tmp/code/reducer.py"


hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.9.0.jar -file /tmp/code/mapper.py -file /tmp/code/reducer.py -input /dados/csv -output /resultado/preco_medio_10 -mapper "python mapper.py" -reducer "python reducer.py"

head -n 10 /\Users\jbati\Documents\GitHub\Projeto-bigData\Projetos\web_Scraping\cvs\1o_Sem_2020__Combustiveis_Automotivos.csv | python mapper.py

Get-Content -Path "C:\Users\jbati\Documents\GitHub\Projeto-bigData\Projetos\web_Scraping\cvs\1o_Sem_2020__Combustiveis_Automotivos.csv" -TotalCount 50 | python2 mapper.py