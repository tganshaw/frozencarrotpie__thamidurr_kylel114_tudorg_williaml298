import sqlite3

DB_NAME = "database.db"

def get_username(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT username FROM userdata WHERE id = {user_id};")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    return cursorfetch

def get_user_id(username):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM userdata WHERE username = \"{username}\";")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    return cursorfetch

def user_exists(username):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM userdata WHERE username = '{username}';")
    cursorfetch = cursor.fetchone()[0]
    db.commit()
    db.close()
    return cursorfetch == 1

def find_user(string):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM userdata WHERE username LIKE '%{string}%';")
    cursorfetch = cursor.fetchall()
    db.commit()
    db.close()
    return cursorfetch
