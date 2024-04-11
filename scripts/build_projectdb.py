"""
Script for creating US accidents database in SQL schema and loading data via
psycopg2 connection to psql server.
"""
import os
from pprint import pprint

import psycopg2 as psql

CREATE_SQL_TABLE_FILE = "create_tables.sql"
IMPORT_SQL_TABLE_FILE = "import_data.sql"
TEST_SQL_FILE = "test_usacc.sql"
DATA_TABLE_FILE = "US_Accidents_sampled_110k.csv"

PORT = "5432"
USER = "team2"
DBNAME = "team2_projectdb"


# Read password from secrets file
file = os.path.join("secrets", ".psql.pass")
with open(file, "r", encoding="utf-8") as file:
    password=file.read().rstrip()


# build connection string
CONN_STRING=f"host=hadoop-04.uni.innopolis.ru port={PORT} user={USER} dbname={DBNAME}\
    password={password}"


# Connect to the remote dbms
with psql.connect(CONN_STRING) as conn:
    # Create a cursor for executing psql commands
    cur = conn.cursor()
    # Read the commands from the file and execute them.
    with open(os.path.join("sql", CREATE_SQL_TABLE_FILE) ,encoding="utf-8") as file:
        content = file.read()
        cur.execute(content)
    conn.commit()

    # Read the commands from the file and execute them.
    with open(os.path.join("sql", IMPORT_SQL_TABLE_FILE) ,encoding="utf-8") as file:
        commands = file.readlines()
        with open(os.path.join("data", DATA_TABLE_FILE), "r", encoding="utf-8") as depts:
            # line 0 - strictly fixed and should not change
            cur.copy_expert(commands[0], depts)

    # If the sql statements are CRUD then you need to commit the change
    conn.commit()

    pprint(conn)
    cur = conn.cursor()
    # Read the sql commands from the file
    with open(os.path.join("sql", TEST_SQL_FILE), encoding="utf-8") as file:
        commands = file.readlines()
        # first line is comment in that file
        for command in commands[1:]:
            cur.execute(command)
            # Read all records and print them
            pprint(cur.fetchall())
