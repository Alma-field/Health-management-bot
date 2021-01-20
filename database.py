from sys import version_info
from string import ascii_lowercase, ascii_uppercase, digits
from random import choices

from flask_sqlalchemy import SQLAlchemy
from flask import abort

from Config import *

if version_info.minor >= 9:
	from datetime import datetime, timedelta
	from zoneinfo import ZoneInfo
	JST = ZoneInfo("Asia/Tokyo")
else:
	from datetime import datetime, timedelta, timezone
	JST = timezone(timedelta(hours=+9), 'JST')

cookie_candidate = digits+ascii_uppercase+ascii_lowercase
pin_candidate = digits

#######################################DB制御
class database():
	def __init__(self, dbname):
		from urllib.parse import urlparse
		self.dbname = dbname#postgres
		url = urlparse(dbname)
		if url.scheme == 'sqlite':#'sqlite://path/[filepath]'
			import sqlite3
			self.conn = sqlite3.connect(url.path)
			self.char = '?'
			self.quotation = '`'
			self.error = sqlite3.InterfaceError
			self.errors = [sqlite3.OperationalError, sqlite3.DatabaseError]
		elif url.scheme == 'mysql':#'mysql://[user]:[password]@[hostname]:[port]/[dbname]'
			import mysql.connector
			self.conn = mysql.connector.connect(
				host = url.hostname,
				port = url.port,
				user = url.username,
				password = url.password,
				database = url.path[1:]
			)
			self.char = '%s'
			self.quotation = '`'
			self.error = mysql.connector.errors.InterfaceError
			self.errors = [mysql.connector.errors.OperationalError, mysql.connector.errors.DatabaseError]
		elif url.scheme == 'postgres':#'postgres://[user]:[password]@[hostname]:[port]/[dbname]'
			import psycopg2
			self.conn = psycopg2.connect(dbname)
			self.char = '%s'
			self.quotation = '"'
			self.error = psycopg2.InterfaceError
			self.errors = [psycopg2.OperationalError, psycopg2.DatabaseError]
		self.c = self.conn.cursor()

	def __del__(self):
		try:
			self.c.close()
		except:
			pass
		try:
			self.conn.close()
		except:
			pass

	def reconnect(self):
		self.__del__()
		try:
			self.__init__(self.dbname)
		except self.error as e:
			return False
		return True

	def is_connected(self, sql):
		if 'is_connected' in dir(self.conn):
			return self.conn.is_connected()
		else:
			try:
				self.c.execute(sql)
				self.c.fetchall()
			except:
				import traceback
				traceback.print_exc()
				return False
		return True

	@staticmethod
	def now_str(pm_day=0, pm_min=0, string=False):#加減する場合の[日/秒]数
		now = datetime.now(tz=JST)
		now = now + timedelta(days=pm_day, minutes=pm_min)
		if string:
			result = now.strftime("%a, %d %b %Y %H:%M:%S JST")
		else:
			result = now.strftime("%Y-%m-%d %H:%M:%S+09:00")
		pm_day, pm_min, string = 0, 0, False
		return result

	@staticmethod
	def generate_cookies(cookie_length=32):
		cookie = ''.join(choices(cookie_candidate, k=cookie_length))
		cookie_length = 32
		return cookie

class line_db(database):
	def __init__(self, dbname):
		super().__init__(dbname)

	def __del__(self):
		super().__del__()

	def user_exists(self, userid):
		sql = "SELECT COUNT(name) FROM users WHERE userid LIKE '%"+userid+"%'"
		self.c.execute(sql)
		count = self.c.fetchone()[0]
		if count == 0:
			return False
		return True

	def user_init(self,userid,name='Noname'):
		username = name
		name = 'Noname'
		status = 'home:none'
		role = 'user'
		liff_status = 'none'
		cache = ''
		sql = f'INSERT INTO users (userid,name,status,role,liff_status,cache) VALUES ({", ".join([self.char]*6)});'
		self.c.execute(sql,(userid,username,status,role,liff_status,cache))
		self.conn.commit()

	def get_user_by_id(self,userid,key=[]):
		if key == []:abort(500)
		if not self.user_exists(userid):
			from line import line_bot_api
			self.user_init(userid,line_bot_api.get_profile(userid).display_name)
		sql = f'SELECT {",".join(map(str,key))} FROM users WHERE userid={self.char}'
		self.c.execute(sql,(userid,))
		result = list(self.c.fetchall())
		if 'tuple' in str(type(result[0])) or 'list' in str(type(result[0])):
			if len(result) != 1:
				for i in range(len(result)):
					if len(key) == 1:
						result[i] = result[i][0]
					else:
						result[i] = list(result[i])
			else:
				if len(key) == 1:
					result = result[0][0]
				else:
					result = list(result[0])
		#print(result)
		return result

	def get_role(self,userid):
		return self.get_user_by_id(userid,['role'])

	def get_userstatus(self,userid):
		return self.get_user_by_id(userid,['status'])

	def set_userstatus(self, userid, status, name):
		self.set_user_by_id(userid, ['name', 'status'], [name, status])

	def set_user_by_id(self, userid, key=[], value=[]):
		if key == [] or value == [] or len(key) != len(value):abort(500)
		setq = []
		for i in range(len(key)):
			string = str(key[i])+'='
			val_type = type(value[i])
			if val_type is int:
				string += str(value[i])
			elif val_type is str:
				string += f'\'{value[i]}\''
			elif 'datetime' in str(val_type):
				string += f'\'{value.strftime("%Y-%m-%d %H:%M:%S+09:00")}\''
			else:
				pass
			setq.append(string)
		setq = ', '.join(setq)
		sql = f'UPDATE users SET {setq} WHERE userid={self.char};'
		key, value = [], []
		self.c.execute(sql, (userid,))
		self.conn.commit()

	def get_users_from_placeid(self, placeid):
		sql = f'SELECT userid FROM users WHERE line_place LIKE \'%,{str(placeid).zfill(3)},%\';'
		self.c.execute(sql)
		try:
			users = list(self.c.fetchone())
		except TypeError as e:
			users = []
		return users

	def set_health_data(self, userid, data):
		today = self.now_str()[:10]
		sql = f'SELECT id FROM condition WHERE userid={self.char} AND date={self.char} LIMIT 1;'
		self.c.execute(sql, (userid, today))
		try:
			id = self.c.fetchone()[0]
			sql = f'UPDATE condition SET '
			sql_l = []
			for i in 'temperature, q1, q2, q3, q4, q5, q6'.split(', '):
				sql_l.append(f'{i}={self.char}')
			sql += ', '.join(sql_l) + f'WHERE id={self.char};'
			self.c.execute(sql, tuple(data+[id]))
		except TypeError as e:
			sql = f'SELECT id FROM condition ORDER BY id DESC LIMIT 1;'
			self.c.execute(sql)
			id = self.c.fetchone()[0]
			sql = f'INSERT INTO condition (id, userid, date, temperature, q1, q2, q3, q4, q5, q6) VALUES ({", ".join([self.char]*10)});'
			self.c.execute(sql, tuple([id, userid, today]+data))
		self.conn.commit()
		return True
