#!/bin/bash

################################
# DOWNLOADING & UNZIPPING DATA #
################################
# clean data folder from zip archives and .csv's
rm -rf data/*.zip
rm -rf data/*.csv

# download archive from my link
url="https://disk.yandex.ru/d/DXY2kxm00i-Alg"

wget "$(yadisk-direct $url)" -O data/data.zip

# unzip (to a single .csv)
unzip data/data.zip -d data/

# remove zip just in case
rm data/data.zip

####################################
# IMPORTING DATABASE TO PostgreSQL #
####################################

# everything happens in this python file
# table is dropped and loaded from new data
python3 scripts/build_projectdb.py

####################################
#     IMPORT TO HDFS VIA SQOOP     #
####################################

# drop old sqoop files from root folder and output
rm -r ./*.avsc
rm -r ./*.avsc
rm -r output/*.avsc
rm -r output/*.java

# delete folders from hdfs
hdfs dfs -rm -r project/warehouse

# read password
sqoop_password=$(head -n 1 secrets/.psql.pass)

# import all tables (single one) via sqoop
sqoop import-all-tables --connect jdbc:postgresql://hadoop-04.uni.innopolis.ru/team2_projectdb \
        --username team2 --password $sqoop_password --compression-codec=snappy --compress --as-avrodatafile \
        --warehouse-dir=project/warehouse --m 1

# move avsc and java files to output folder
mv *.avsc output/
mv *.java output/

# put avsc schemas to hdfs
hdfs dfs -mkdir -p project/warehouse/avsc
hdfs dfs -put output/*.avsc project/warehouse/avsc
