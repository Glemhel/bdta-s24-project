#!/bin/bash

# QUERY NUMBER: 2

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q2
hdfs dfs -rm -r project/output/q2
rm -rf output/q2.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q2.hql

# Add a header to the output file
echo "Hour,Severity,AccidentCount" > output/q2.csv
# concatenate all file partitions and 
# append the output to the file output/q2.csv
hdfs dfs -cat project/output/q2/* >> output/q2.csv