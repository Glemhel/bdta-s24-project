-- create single table of US Accidents database
START TRANSACTION;

-- drop table altogether if exists
DROP TABLE IF EXISTS us_accidents;

-- add US Accidents main (only) table
CREATE TABLE IF NOT EXISTS us_accidents (
    ID SERIAL PRIMARY KEY NOT NULL,
    ID_STR VARCHAR(16) NOT NULL,
    Source VARCHAR(10) NOT NULL,
    Severity SMALLINT NOT NULL,
    Start_Time TIMESTAMP NOT NULL,
    End_Time TIMESTAMP NOT NULL,
    Start_Lat DOUBLE PRECISION NOT NULL,
    Start_Lng DOUBLE PRECISION NOT NULL,
    End_Lat DOUBLE PRECISION,
    End_Lng DOUBLE PRECISION,
    Distance_mi DOUBLE PRECISION NOT NULL,
    Description TEXT,
    Street VARCHAR(255),
    City VARCHAR(255),
    County VARCHAR(255) NOT NULL,
    State CHAR(2) NOT NULL,
    Zipcode VARCHAR(32),
    Country CHAR(2) NOT NULL,
    Timezone VARCHAR(255),
    Airport_Code CHAR(8),
    Weather_Timestamp TIMESTAMP,
    Temperature_F FLOAT,
    Wind_Chill_F FLOAT,
    Humidity_Percent FLOAT,
    Pressure_in FLOAT,
    Visibility_mi FLOAT,
    Wind_Direction VARCHAR(10),
    Wind_Speed_mph FLOAT,
    Precipitation_in FLOAT,
    Weather_Condition VARCHAR(40),
    Amenity BOOLEAN NOT NULL,
    Bump BOOLEAN NOT NULL,
    Crossing BOOLEAN NOT NULL,
    Give_Way BOOLEAN NOT NULL,
    Junction BOOLEAN NOT NULL,
    No_Exit BOOLEAN NOT NULL,
    Railway BOOLEAN NOT NULL,
    Roundabout BOOLEAN NOT NULL,
    Station BOOLEAN NOT NULL,
    Stop BOOLEAN NOT NULL,
    Traffic_Calming BOOLEAN NOT NULL,
    Traffic_Signal BOOLEAN NOT NULL,
    Turning_Loop BOOLEAN NOT NULL,
    Sunrise_Sunset VARCHAR(10),
    Civil_Twilight VARCHAR(10),
    Nautical_Twilight VARCHAR(10),
    Astronomical_Twilight VARCHAR(10)
);

-- set timestamp format
ALTER DATABASE team2_projectdb SET datestyle TO iso, ymd;

COMMIT;