import os
import Config
from database import line_db

dbname = os.environ["DATABASE_URL"]
db = line_db(dbname)

sql = """
CREATE TABLE users (
	userid text NOT NULL,
	name text NOT NULL,
	status text NOT NULL,
	role text NOT NULL,
	liff_status text NOT NULL,
	cache text NOT NULL,
	showname text NOT NULL,
	CONSTRAINT users_pkey PRIMARY KEY (userid)
);
"""
#db.c.execute(sql)

sql = """
CREATE TABLE department (
	id text NOT NULL,
	name text NOT NULL,
	CONSTRAINT department_pkey PRIMARY KEY (id)
);
"""
#sql = "DROP TABLE department;"
#db.c.execute(sql)

sql = """
CREATE TABLE condition (
	id integer NOT NULL,
	userid text NOT NULL,
	date date NOT NULL,
	temperature numeric NOT NULL,
	q1 boolean NOT NULL,
	q2 boolean NOT NULL,
	q3 boolean NOT NULL,
	q4 boolean NOT NULL,
	q5 boolean NOT NULL,
	q6 boolean NOT NULL,
	CONSTRAINT condition_pkey PRIMARY KEY (id)
);
INSERT INTO condition (id, userid, date, temperature, q1, q2, q3, q4, q5, q6) VALUES (0, \'\', \'2021-01-01\', 0.0, false, false, false, false, false, false);
"""
#sql = "DROP TABLE condition;"
#db.c.execute(sql)

sql = """
CREATE TABLE config (
	temperature_check BOOLEAN NOT NULL,
	temperature numeric NOT NULL,
	question_check BOOLEAN NOT NULL,
	question integer NOT NULL
);
"""
sql = 'INSERT INTO config (temperature_check, temperature, question_check, question) VALUES (\'true\', 37.5, \'true\', 1);'
sql = 'UPDATE config SET temperature=37.0;'
db.c.execute(sql)

db.conn.commit()

del db
