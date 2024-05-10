USE team2_projectdb;

DROP TABLE IF EXISTS q7_results;
CREATE EXTERNAL TABLE q7_results(
 id INT,
    id_str STRING,
    source STRING,
    severity INT,
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
    weather_timestamp TIMESTAMP,
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
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
location 'project/hive/warehouse/q7';

INSERT INTO q7_results
SELECT id, id_str, source, severity,
       start_time,
       end_time,
       start_lat, start_lng, end_lat,
       end_lng, distance_mi, description, street, city, county,
       state, zipcode, country, timezone, airport_code, weather_timestamp,
       temperature_f, wind_chill_f, humidity_percent, pressure_in, visibility_mi,
       wind_direction, wind_speed_mph, precipitation_in, weather_condition, amenity, bump,
       crossing, give_way, junction, no_exit, railway, roundabout, station, stop, traffic_calming,
       traffic_signal, turning_loop, sunrise_sunset, civil_twilight, nautical_twilight, astronomical_twilight 
FROM us_accidents1 LIMIT 10;

INSERT OVERWRITE DIRECTORY 'project/output/q7'
ROW FORMAT DELIMITED FIELDS
TERMINATED BY ','
SELECT * FROM q7_results;
