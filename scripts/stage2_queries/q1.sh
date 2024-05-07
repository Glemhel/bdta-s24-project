#!/bin/bash

# QUERY NUMBER: 1

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q1
hdfs dfs -rm -r project/output/q1
rm -rf output/q1.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q1.hql

# Add a header to the output file
echo "Severity,SeverityCount" > output/q1.csv
# concatenate all file partitions and 
# append the output to the file output/q1.csv
hdfs dfs -cat project/output/q1/* >> output/q1.csv