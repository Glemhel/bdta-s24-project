#!/bin/bash

# QUERY NUMBER: 6

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q6
hdfs dfs -rm -r project/output/q6
rm -rf output/q6.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q6.hql

# Add a header to the output file
echo "IncidentDuration,Severity" > output/q6.csv
# concatenate all file partitions and 
# append the output to the file output/q6.csv
hdfs dfs -cat project/output/q6/* >> output/q6.csv