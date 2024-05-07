#!/bin/bash

# QUERY NUMBER: 4

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q4
hdfs dfs -rm -r project/output/q4
rm -rf output/q4.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q4.hql

# Add a header to the output file
echo "StateID,State,Severity,AccidentCount" > output/q4.csv
# concatenate all file partitions and 
# append the output to the file output/q4.csv
hdfs dfs -cat project/output/q4/* >> output/q4.csv