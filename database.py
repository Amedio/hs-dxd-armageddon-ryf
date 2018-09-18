import os
import psycopg2

database_url = os.environ['DATABASE_URL']

def insert_char(shortcut, name, thumbnail):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO character (shortcut, name, thumbnail) VALUES ('{0}', '{1}', '{2}')".format(shortcut, name, thumbnail))

    conn.commit()
    cur.close()
    conn.close()

def select_char(shortcut):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE shortcut = '{0}'".format(shortcut))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row