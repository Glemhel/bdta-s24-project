USE team2_projectdb;

DROP TABLE IF EXISTS q5_results;
CREATE EXTERNAL TABLE q5_results(
Month INT,
MonthName STRING,
Severity INT,
AccidentCount INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q5';

INSERT INTO q5_results
SELECT 
  MONTH(start_time) AS Month,
  CASE MONTH(start_time)
    WHEN 1 THEN 'January'
    WHEN 2 THEN 'February'
    WHEN 3 THEN 'March'
    WHEN 4 THEN 'April'
    WHEN 5 THEN 'May'
    WHEN 6 THEN 'June'
    WHEN 7 THEN 'July'
    WHEN 8 THEN 'August'
    WHEN 9 THEN 'September'
    WHEN 10 THEN 'October'
    WHEN 11 THEN 'November'
    WHEN 12 THEN 'December'
  END AS MonthName,
  Severity,
  COUNT(*) AS AccidentCount
FROM us_accidents1
GROUP BY MONTH(start_time), 
         CASE MONTH(start_time)
           WHEN 1 THEN 'January'
           WHEN 2 THEN 'February'
           WHEN 3 THEN 'March'
           WHEN 4 THEN 'April'
           WHEN 5 THEN 'May'
           WHEN 6 THEN 'June'
           WHEN 7 THEN 'July'
           WHEN 8 THEN 'August'
           WHEN 9 THEN 'September'
           WHEN 10 THEN 'October'
           WHEN 11 THEN 'November'
           WHEN 12 THEN 'December'
         END,
         Severity
ORDER BY Month, Severity;

INSERT OVERWRITE DIRECTORY 'project/output/q5'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q5_results;