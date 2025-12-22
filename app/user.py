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
    print(username)
    cursor.execute(f"SELECT id FROM userdata WHERE username = '{username}';")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    return cursorfetch


def get_cards(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT cards FROM userdata WHERE id = {user_id};")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    if(cursorfetch is not None and cursorfetch != -1):
        return cursorfetch.split(";")
    return -1

def get_deck(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT deck FROM userdata WHERE id = {user_id};")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    if(cursorfetch is not None and cursorfetch != -1):
        return cursorfetch.split(";")
    return -1

def add_card_to_deck(user_id, card_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cards = get_cards(user_id)
    deck = get_deck(user_id)
    print(cards)
    if cards == -1: # if user has no cards
        return -1
    else:
        if card_id not in cards: # if card is not in user's deck
            return -1

        if deck == -1: # if deck is empty
            cursor.execute(f"UPDATE userdata SET deck = \"{card_id}\" WHERE id = {user_id};")
        else:
            if card_id not in deck: # if card is not already in the deck
                temp = ""
                for c in deck:
                    temp+=f"{c};"
                cursor.execute(f"UPDATE userdata SET deck = \"{temp}{card_id}\" WHERE id = {user_id};")
    db.commit()
    db.close()

def add_card(user_id, card_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cards = get_cards(user_id)
    if cards == -1:
        print(card_id)
        cursor.execute(f"UPDATE userdata SET cards = \"{card_id}\" WHERE id = {user_id};")
    else:
        if card_id not in cards:
            temp = ""
            if cards != -1:
                for c in cards:
                    temp+=f"{c};"
                cards = temp[:-1]
            if cards != -1:
                cursor.execute(f"UPDATE userdata SET cards = \"{cards};{card_id}\" WHERE id = {user_id};")
            else:
                cursor.execute(f"UPDATE userdata SET cards = \"{card_id}\" WHERE id = {user_id};")
    db.commit()
    db.close()

def remove_cards(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"UPDATE userdata SET cards = NULL WHERE id = {user_id};")
    db.commit()
    db.close()

def remove_card_from_deck(user_id, card_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    deck = get_deck(user_id)
    if deck != -1:
        if card_id not in deck:
            return -1
        deck.remove(card_id)
        deck = ";".join(deck)
        cursor.execute(f"UPDATE userdata SET deck = '{deck}' WHERE id = {user_id}")
    else:
        return -1
    db.commit()
    db.close()

def remove_deck(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"UPDATE userdata SET deck = NULL WHERE id = {user_id};")
    db.commit()
    db.close()

def get_currency(user_id):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(f"SELECT currency FROM userdata WHERE id = {user_id};")
    cursorfetch = cursor.fetchone()
    if(cursorfetch is not None):
        cursorfetch = cursorfetch[0]
    else:
        cursorfetch = -1
    db.commit()
    db.close()
    return cursorfetch

def add_currency(user_id, amt):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    currency = get_currency(user_id)
    if int(currency) + int(amt) <= 9999:
        cursor.execute(f"UPDATE userdata SET currency = {int(currency) + int(amt)} WHERE id = {user_id};")
    else:
        cursor.execute(f"UPDATE userdata SET currency = 9999 WHERE id = {user_id};")
    db.commit()
    db.close()

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
    temp = ""
    for i in string:
        if i != "\"" and i != "'":
            temp += i
    string = temp
    cursor.execute(f"SELECT * FROM userdata WHERE username LIKE '%{string}%';")
    cursorfetch = cursor.fetchall()
    db.commit()
    db.close()
    return cursorfetch
