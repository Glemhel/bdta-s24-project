USE team2_projectdb;

DROP TABLE IF EXISTS q2_results;
CREATE EXTERNAL TABLE q2_results(
Hour INT,
Severity INT,
AccidentCount INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q2';

INSERT INTO q2_results
SELECT HOUR(start_time) AS Hour, Severity, COUNT(*) AS AccidentCount
FROM us_accidents1
GROUP BY HOUR(start_time), Severity;

INSERT OVERWRITE DIRECTORY 'project/output/q2'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q2_results;