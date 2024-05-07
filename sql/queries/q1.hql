USE team2_projectdb;

DROP TABLE IF EXISTS q1_results;
CREATE EXTERNAL TABLE q1_results(
Severity INT,
SeverityCount INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q1';

INSERT INTO q1_results
SELECT Severity, COUNT(*) AS SeverityCount
FROM us_accidents1
GROUP BY Severity;

INSERT OVERWRITE DIRECTORY 'project/output/q1'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q1_results;