import os
import psycopg2
from model.character import Character

database_url = os.environ['DATABASE_URL']

def exists_shortcut(shortcut):
    player_character = get_shortcut(shortcut)

    return player_character != None

def exists_player(player):
    player_character = get_player(player)

    return player_character != None

def insert(shortcut, name, thumbnail, player):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO character (shortcut, name, thumbnail, player) VALUES ('{0}', '{1}', '{2}', '{3}')".format(shortcut, name, thumbnail, player))

    conn.commit()
    cur.close()
    conn.close()

def update(shortcut, name, thumbnail):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("UPDATE character SET (name, thumbnail) = ('{1}', '{2}') WHERE shortcut = '{0}'".format(shortcut, name, thumbnail))

    conn.commit()
    cur.close()
    conn.close()

def get_shortcut(shortcut):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE shortcut = '{0}'".format(shortcut))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row != None:
        player_character = Character(row[1], row[2], row[3], row[4])
        return player_character

    return None

def get_player(player):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE player = '{0}'".format(player))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row != None:
        player_character = Character(row[1], row[2], row[3], row[4])
        return player_character

    return None