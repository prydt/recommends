import sqlite3
con = sqlite3.connect('recommends.db')
cur = con.cursor()
cur.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username VARCHAR(15), hash BLOB)')
cur.execute('CREATE TABLE items(user_id INTEGER, category VARCHAR(20), name VARCHAR(255))')