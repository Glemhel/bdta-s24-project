COPY us_accidents FROM STDIN WITH CSV HEADER DELIMITER ',';
-- XXX: if number of lines changes, one should also change build_projectdb command order!
-- We do not have None or escaping specified as per dataset format
-- COPY DATA FROM STDIN
