import os
import Config
from database import database

dbname = os.environ["DATABASE_URL"]
db = database(dbname)

sql = """
CREATE TABLE users (
	userid text NOT NULL,
	name text NOT NULL,
	status text NOT NULL,
	role text NOT NULL,
	liff_status text NOT NULL,
	cache text,
	CONSTRAINT users_pkey PRIMARY KEY (userid)
);
"""
#db.c.execute(sql)

sql = """
CREATE TABLE department (
	id text NOT NULL,
	level integer NOT NULL,
	name text NOT NULL,
	CONSTRAINT department_pkey PRIMARY KEY (id)
);
"""
#db.c.execute(sql)

sql = """
CREATE TABLE condition (
	id integer NOT NULL,
	temperature numeric NOT NULL,
	q1 boolean NOT NULL,
	q2 boolean NOT NULL,
	q3 boolean NOT NULL,
	q4 boolean NOT NULL,
	q5 boolean NOT NULL,
	q6 boolean NOT NULL,
	userid text NOT NULL,
	CONSTRAINT condition_pkey PRIMARY KEY (id)
);
"""
#sql = "DROP TABLE condition;"
db.c.execute(sql)

db.conn.commit()
