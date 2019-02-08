import os
import psycopg2
from model.character import Character

database_url = os.environ['DATABASE_URL']

def exists_shortcut(shortcut):
    player_character = get_shortcut(shortcut)

    return player_character != None

def exists_shortcut_guild(shortcut, guild_id):
    player_character = get_shortcut_guild(shortcut, guild_id)

    return player_character != None

def exists_player(player):
    player_character = get_player(player)

    return player_character != None

def exists_player_guild(player, guild_id):
    player_character = get_player_guild(player, guild_id)

    return player_character != None

def insert(shortcut, name, thumbnail, player, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO character (shortcut, name, thumbnail, player, guild_id) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(shortcut, name, thumbnail, player, guild_id))

    conn.commit()
    cur.close()
    conn.close()

def update(shortcut, name, thumbnail, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("UPDATE character SET (name, thumbnail) = ('{1}', '{2}') WHERE shortcut = '{0}' AND guild_id = '{3}'".format(shortcut, name, thumbnail, guild_id))

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

def get_shortcut_guild(shortcut, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE shortcut = '{0}' AND guild_id = '{1}'".format(shortcut, guild_id))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row != None:
        player_character = Character(row[1], row[2], row[3], row[4])
        return player_character

    return None

def get_shortcut_player_guild(shortcut, player, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE shortcut = '{0}' AND player = '{1}' AND guild_id = '{2}'".format(shortcut, player, guild_id))

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

def get_player_guild(player, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE player = '{0}' AND guild_id = '{1}'".format(player, guild_id))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row != None:
        player_character = Character(row[1], row[2], row[3], row[4])
        return player_character

    return None

def get_all_player(player, guild_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM character WHERE player = '{0}' AND guild_id = '{1}'".format(player, guild_id))

    row = cur.fetchone()

    player_characters = []

    while row != None:
        player_character = Character(row[1], row[2], row[3], row[4])
        player_characters.append(player_character)
        
        row = cur.fetchone()

    cur.close()
    conn.close()

    return player_characters