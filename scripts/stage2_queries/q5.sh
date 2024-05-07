#!/bin/bash

# QUERY NUMBER: 5

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q5
hdfs dfs -rm -r project/output/q5
rm -rf output/q5.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q5.hql

# Add a header to the output file
echo "Month,MonthName,Severity,AccidentCount" > output/q5.csv
# concatenate all file partitions and 
# append the output to the file output/q5.csv
hdfs dfs -cat project/output/q5/* >> output/q5.csv