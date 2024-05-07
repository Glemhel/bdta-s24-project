#!/bin/bash

# QUERY NUMBER: 3

################################
#  QUERIES OUTPUT PREPARATION  #
################################
hdfs dfs -rm -r project/hive/warehouse/q3
hdfs dfs -rm -r project/output/q3
rm -rf output/q3.csv

# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $HIVE_PASSWORD -f sql/queries/q3.hql

# Add a header to the output file
echo "Weekday,WeekdayName,Severity,AccidentCount" > output/q3.csv
# concatenate all file partitions and 
# append the output to the file output/q3.csv
hdfs dfs -cat project/output/q3/* >> output/q3.csv