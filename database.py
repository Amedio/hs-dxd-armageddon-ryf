import os
import psycopg2

database_url = os.environ['DATABASE_URL']

def insert_char(shortcut, name, thumbnail, player):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO character (shortcut, name, thumbnail, player) VALUES ('{0}', '{1}', '{2}', '{3}')".format(shortcut, name, thumbnail, player))

    conn.commit()
    cur.close()
    conn.close()

def select_char_shortcut(shortcut):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE shortcut = '{0}'".format(shortcut))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row

def select_char_player(player):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE player = '{0}'".format(player))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row