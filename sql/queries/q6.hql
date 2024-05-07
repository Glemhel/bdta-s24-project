USE team2_projectdb;

DROP TABLE IF EXISTS q6_results;
CREATE EXTERNAL TABLE q6_results(
  IncidentDuration DOUBLE,
  Severity INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q6';

INSERT INTO q6_results
SELECT 
  UNIX_TIMESTAMP(End_Time) - UNIX_TIMESTAMP(Start_Time) AS IncidentDuration,
  Severity
FROM us_accidents1;

INSERT OVERWRITE DIRECTORY 'project/output/q6'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q6_results;
