import os
import psycopg2
from model.memberrole import MemberRole

database_url = os.environ['DATABASE_URL']

def exists(member_id):
    return get(member_id) != None

def insert(member_id, guild_id, role):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("INSERT INTO member_role (member_id, guild_id, role) VALUES ('{0}', '{1}', '{2}')".format(member_id, guild_id, role))

    conn.commit()
    cur.close()
    conn.close()

def update(member_id, role):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("UPDATE member_role SET (role) = ('{1}') WHERE member_id = '{0}'".format(member_id, role))

    conn.commit()
    cur.close()
    conn.close()

def get(member_id):
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM member_role WHERE member_id = '{0}'".format(member_id))

    row = cur.fetchone()

    cur.close()
    conn.close()
    
    if row != None:
        member_role = MemberRole(row[1], row[2], row[3])
        return member_role

    return None
    
def admin():
    conn = psycopg2.connect(database_url, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM member_role WHERE role = 'admin'")

    row = cur.fetchone()

    cur.close()
    conn.close()
    
    if row != None:
        member_role = MemberRole(row[1], row[2], row[3])
        return member_role

    return None
