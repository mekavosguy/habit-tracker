import os, psycopg2, psycopg2.extras
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='public')

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS habits (
          id SERIAL PRIMARY KEY,
          name TEXT NOT NULL,
          icon TEXT DEFAULT '🌟',
          tag TEXT DEFAULT 'focus'
        );
        CREATE TABLE IF NOT EXISTS checks (
          id SERIAL PRIMARY KEY,
          habit_id INT NOT NULL,
          year INT, month INT, day INT,
          UNIQUE(habit_id, year, month, day)
        );
    ''')
    cur.execute('SELECT COUNT(*) FROM habits')
    if cur.fetchone()[0] == 0:
        cur.executemany(
          'INSERT INTO habits(name,icon,tag) VALUES(%s,%s,%s)',
          [('Morning run','🏃','body'),('Read 30 min','📖','focus'),
           ('Drink 2L water','💧','health'),('Meditate','🧘','focus'),
           ('Eat clean','🥗','health')]
        )
    conn.close()

init_db()
