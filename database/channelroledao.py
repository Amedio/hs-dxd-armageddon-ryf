import os
import psycopg2
from model.channelrole import ChannelRole

database_url = os.environ['DATABASE_URL']

def exists(channel_id):
    return get(channel_id) != None

def insert(channel_id, guild_id, role):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO channel_role (channel_id, guild_id, role) VALUES ('{0}', '{1}', '{2}')".format(channel_id, guild_id, role))

    conn.commit()
    cur.close()
    conn.close()

def update(channel_id, role):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("UPDATE channel_role SET (role) = ('{1}') WHERE channel_id = '{0}'".format(channel_id, role))

    conn.commit()
    cur.close()
    conn.close()

def get(channel_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM channel_role WHERE channel_id = '{0}'".format(channel_id))

    row = cur.fetchone()

    cur.close()
    conn.close()
    
    if row != None:
        channel_role = ChannelRole(row[1], row[2], row[3])
        return channel_role

    return None
def combat():
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM channel_role WHERE role = 'combat'")

    row = cur.fetchone()

    cur.close()
    conn.close()
    
    if row != None:
        channel_role = ChannelRole(row[1], row[2], row[3])
        return channel_role

    return None
