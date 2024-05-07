#!/bin/bash

# delete hive folder
hdfs dfs -rm -r project/hive
# delete hive_results output
rm -r output/hive_results.txt

# Import secret password
password=$(head -n 1 secrets/.hive.pass)
# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $password -f sql/db.hql > output/hive_results.txt
