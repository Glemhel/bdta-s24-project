-- Importing data from hdfs to Hive via HiveQL queries

-- enable dynamic partitioning
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
SET hive.execution.engine=tez;

-- drop database from hive if exists for clear restart
DROP DATABASE IF EXISTS team2_projectdb CASCADE;

-- create database and use it
CREATE DATABASE team2_projectdb LOCATION "project/hive/warehouse";
USE team2_projectdb;

-- Create us_accidents table
CREATE EXTERNAL TABLE us_accidents
    STORED AS AVRO LOCATION 'project/warehouse/us_accidents'
    TBLPROPERTIES ('avro.schema.url'='project/warehouse/avsc/us_accidents.avsc');

-- Sample query
SELECT * FROM us_accidents LIMIT 5;

-- I check hiveql datatypes with DESCRIBE and they are all fine - add to report!

-- create partitioned and bucketed table
CREATE EXTERNAL TABLE us_accidents1 (
    id INT,
    id_str STRING,
    source STRING,
--    severity INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    start_lat DOUBLE,
    start_lng DOUBLE,
    end_lat DOUBLE,
    end_lng DOUBLE,
    distance_mi DOUBLE,
    description STRING,
    street STRING,
    city STRING,
    county STRING,
    state STRING,
    zipcode STRING,
    country STRING,
    timezone STRING,
    airport_code STRING,
    weather_timestamp BIGINT,
    temperature_f DOUBLE,
    wind_chill_f DOUBLE,
    humidity_percent DOUBLE,
    pressure_in DOUBLE,
    visibility_mi DOUBLE,
    wind_direction STRING,
    wind_speed_mph DOUBLE,
    precipitation_in DOUBLE,
    weather_condition STRING,
    amenity BOOLEAN,
    bump BOOLEAN,
    crossing BOOLEAN,
    give_way BOOLEAN,
    junction BOOLEAN,
    no_exit BOOLEAN,
    railway BOOLEAN,
    roundabout BOOLEAN,
    station BOOLEAN,
    stop BOOLEAN,
    traffic_calming BOOLEAN,
    traffic_signal BOOLEAN,
    turning_loop BOOLEAN,
    sunrise_sunset STRING,
    civil_twilight STRING,
    nautical_twilight STRING,
    astronomical_twilight STRING
)
    PARTITIONED BY (severity int)
    CLUSTERED BY (state) into 5 buckets
    STORED AS AVRO LOCATION 'project/hive/warehouse/us_accidents1'
    TBLPROPERTIES ('AVRO.COMPRESS'='SNAPPY');

-- insert data from unpartitioned table
INSERT INTO us_accidents1
SELECT id, id_str, source,
       start_time,
       end_time,
       start_lat, start_lng, end_lat,
       end_lng, distance_mi, description, street, city, county,
       state, zipcode, country, timezone, airport_code, weather_timestamp,
       temperature_f, wind_chill_f, humidity_percent, pressure_in, visibility_mi,
       wind_direction, wind_speed_mph, precipitation_in, weather_condition, amenity, bump,
       crossing, give_way, junction, no_exit, railway, roundabout, station, stop, traffic_calming,
       traffic_signal, turning_loop, sunrise_sunset, civil_twilight, nautical_twilight, astronomical_twilight,
       severity 
FROM us_accidents;

-- drop initial table
DROP TABLE us_accidents;

-- try to query some data from the partitioned table
SELECT * FROM us_accidents1 WHERE severity=3 AND state="FL" LIMIT 10;

