#!/bin/bash

################################
#   HIVE TABLES PREPARATIONS   #
################################

# delete hive folder
hdfs dfs -rm -r project/hive
# delete hive_results output
rm -r output/hive_results.txt

#################################################
#   CREATE HIVE PARTITIONED & BUCKETED TABLES   #
#################################################

# Import secret password
password=$(head -n 1 secrets/.hive.pass)
# Use beeline to import from hdfs to Hive via sql/db.hql
beeline -u jdbc:hive2://hadoop-03.uni.innopolis.ru:10001 -n team2 -p $password -f sql/db.hql > output/hive_results.txt

#################
#  RUN QUERIES  #
#################

# Directory containing the scripts
SCRIPT_DIR="scripts/stage2_queries"

# Check if the directory exists
if [ ! -d "$SCRIPT_DIR" ]; then
  echo "Directory $SCRIPT_DIR does not exist."
  exit 1
fi

# Read the password from secrets/.hive.pass
password=$(head -n 1 secrets/.hive.pass)
if [ -z "$password" ]; then
  echo "Password could not be read from secrets/.hive.pass"
  exit 1
fi

# Loop through and execute each script in the directory
for script in "$SCRIPT_DIR"/*; do
  if [ -x "$script" ] && [ -f "$script" ]; then
    echo "Running $script..."
    # Export the password as an environment variable and run the script
    HIVE_PASSWORD="$password" bash "$script"
  else
    echo "Skipping $script: not an executable file."
  fi
done