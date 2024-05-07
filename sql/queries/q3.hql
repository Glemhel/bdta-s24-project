USE team2_projectdb;

DROP TABLE IF EXISTS q3_results;
CREATE EXTERNAL TABLE q3_results(
Weekday INT,
WeekdayName STRING,
Severity INT,
AccidentCount INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q3';

INSERT INTO q3_results
SELECT 
  CASE DAYOFWEEK(start_time)
    WHEN 2 THEN 1
    WHEN 3 THEN 2
    WHEN 4 THEN 3
    WHEN 5 THEN 4
    WHEN 6 THEN 5
    WHEN 7 THEN 6
    WHEN 1 THEN 7
  END AS Weekday,
  CASE DAYOFWEEK(start_time)
    WHEN 2 THEN 'Monday'
    WHEN 3 THEN 'Tuesday'
    WHEN 4 THEN 'Wednesday'
    WHEN 5 THEN 'Thursday'
    WHEN 6 THEN 'Friday'
    WHEN 7 THEN 'Saturday'
    WHEN 1 THEN 'Sunday'
  END AS WeekdayName,
  Severity,
  COUNT(*) AS AccidentCount
FROM us_accidents1
GROUP BY 
  CASE DAYOFWEEK(start_time)
    WHEN 2 THEN 1
    WHEN 3 THEN 2
    WHEN 4 THEN 3
    WHEN 5 THEN 4
    WHEN 6 THEN 5
    WHEN 7 THEN 6
    WHEN 1 THEN 7
  END,
  CASE DAYOFWEEK(start_time)
    WHEN 2 THEN 'Monday'
    WHEN 3 THEN 'Tuesday'
    WHEN 4 THEN 'Wednesday'
    WHEN 5 THEN 'Thursday'
    WHEN 6 THEN 'Friday'
    WHEN 7 THEN 'Saturday'
    WHEN 1 THEN 'Sunday'
  END,
  Severity
ORDER BY Weekday;

INSERT OVERWRITE DIRECTORY 'project/output/q3'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q3_results;