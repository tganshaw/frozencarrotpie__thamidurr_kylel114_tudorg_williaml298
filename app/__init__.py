from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import *
import urllib
import os
import json
import sqlite3
import user
import card
import random

DB_NAME = "database.db"
DB = sqlite3.connect(DB_NAME)
DB_CURSOR = DB.cursor()

DB_CURSOR.execute("CREATE TABLE IF NOT EXISTS userdata(username TEXT, password TEXT, cards TEXT, deck TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT);")

app = Flask(__name__)

app.secret_key = "83ut83ojreoikdlshg3958u4wjtse09gol.hi"
#
# @app.route("/profile")
# def homepage():
#     if 'username' not in session:
#         return render_template("login.html")
#
#     if(not user.user_exists(session['username'])):
#         return redirect("/logout")
#
#     DB = sqlite3.connect(DB_NAME)
#     DB_CURSOR = DB.cursor()
#
#     DB_CURSOR.execute(f"SELECT id FROM userdata WHERE username =\"{session['username']}\";")
#     userId = DB_CURSOR.fetchone()[0]
#     session['userId'] = userId
#     numBlogs = blog.get_num_blogs(userId)
#     arr = blog.get_blog_links(userId)
#     return render_template("userprofile.html", username = session["username"], numblogs = numBlogs, blogs = blog.get_blogs(userId), txt = arr, owner = "true")

#----------------------------------------------------------

@app.route("/")
def homepagehtml():
    loggedIn = "false"
    if 'username' in session:
        if user.get_user_id(session['username']) == -1:
            return redirect("/login.html")
        user_id = user.get_user_id(session['username'])
        cards = user.get_cards(user_id)
        deck = user.get_deck(user_id)

        return render_template("homepage.html", test = cards, test2 = deck)
    else:
        return redirect("/login.html")


    return render_template("homepage.html",logged_in = loggedIn)

#----------------------------------------------------------

@app.route("/pull", methods = ["POST", "GET"])
def pull():
    if 'username' in session:
        if 'count' in request.args:
            num_pulls = int(request.args['count'])
        else:
            num_pulls = 1
        user_id = user.get_user_id(session['username'])
        for i in range (num_pulls):
            if "set" not in request.args:
                random_set = random.choice(os.listdir("data"))
                random_set = random_set[:-5]
            else:
                random_set = request.args['set']
            file = open(f"data/{random_set}.json", "r")
            data = json.load(file)["cards"]
            random_card = random.choice(data)
            while random_card == data[0]:
                random_card = random.choice(data)
            random_card = random_card["id"]

            user.add_card(user_id,random_card)
        if "set" in request.args:
            return redirect(f"/displayset?SET={request.args['set']}")
        return redirect("/")
    return redirect("/")

#----------------------------------------------------------

@app.route("/removecards", methods=["POST","GET"])
def remove_cards():
    user_id = user.get_user_id(session["username"])
    user.remove_cards(user_id)
    user.remove_deck(user_id)
    return redirect("/")

#----------------------------------------------------------

@app.route("/remove_deck", methods=["POST","GET"])
def remove_from_deck():
    user_id = user.get_user_id(session["username"])
    user.remove_card_from_deck(user_id, request.args["id"])
    return redirect(f"/card/{request.args['id']}")

#----------------------------------------------------------

@app.route("/add_deck", methods=["POST","GET"])
def add_to_deck():
    if "id" not in request.args:
        return redirect("/")

    card_id = request.args["id"]
    user_id = user.get_user_id(session["username"])
    user.add_card_to_deck(user_id,card_id)
    return redirect(f"/card/{card_id}")


#----------------------------------------------------------

@app.route("/displayset", methods=["POST","GET"])
def displayset():
    if 'username' not in session:
        return redirect("/")
    if "SET" in request.args:
        set_id = request.args["SET"]
        if os.path.exists(f"data/{set_id}.json"):
            file = open(f"data/{set_id}.json", "r")
            data = json.load(file)
        else:
            return "Set doesn't exist. Sorry"

        user_cards = user.get_cards(user.get_user_id(session["username"]))
        set_data = data
        data = data["cards"]

        title_data = ""
        title_data += f"{set_data['name']}"
        if "logo" in set_data:
            title_data += f"<img class='h-[38px] w-[38px]'src = {set_data['logo']}><br><br>"
        title_data += f"<a href='/pull?set={set_id}'>Pull</a><br>"
        title_data += f"<a href='/pull?set={set_id}&count=10'>Pull x10</a>"
        img_data = ""
        for card in data:
            if not isinstance(card,int):
                grayscale = "grayscale"
                if not isinstance(user_cards, int):
                    if card['id'] in user_cards:
                        grayscale = "grayscale-0"
                if "image" in card:
                # img_data += f"<a href='{card["image"]}/high.png' target = _blank>"
                    img_data += f"<a href='card/{card['id']}'>"
                    img_data += f"<img src = '{card['image']}/low.png' loading='lazy' class='{grayscale}'><br>\n"
                    img_data += "</a>"
                else:
                    img_data += f"<a href='card/{card['id']}'>"
                    img_data += f"<img src = 'static/noimglow.png' loading='lazy' ><br>\n"
                    img_data += "</a>"
    else:
        return redirect("/")
    return render_template("collection.html", imgs = img_data, title = title_data)

#----------------------------------------------------------

@app.route("/displaycollection")
def display_collection():
    if "username" in session:
        user_id = user.get_user_id(session["username"])
        img_data = ""
        cards_list = user.get_deck(user_id)
        if isinstance(cards_list,int):
            img_data = "You have no cards."
            return render_template("collection.html", imgs = img_data)
        for each_card in cards_list:
            info_arr = each_card.split("-")
            set_id = ""
            local_id = info_arr[-1]

            for i in info_arr:
                if i != local_id:
                    set_id += f"{i}-"
            set_id = set_id[:-1]
            if("SWSH" in local_id):
                local_id = local_id[4:]
            if("BW" in local_id or "XY" in local_id or "SM" in local_id or "SV" in local_id):
                local_id = local_id[2:]
            local_id = str(card.correct_card_id_backwards(int(local_id), set_id))

            if os.path.exists(f"data/{set_id}.json"):
                file = open(f"data/{set_id}.json", "r")
                data = json.load(file)["cards"][int(local_id)]
                if "image" in data:
                # img_data += f"<a href='{card["image"]}/high.png' target = _blank>"
                    img_data += f"<a href='card/{data['id']}'>"
                    img_data += f"<img src = '{data['image']}/low.png' loading='lazy'><br>\n"
                    img_data += "</a>"
                else:
                    img_data += f"<a href='card/{data['id']}'>"
                    img_data += f"<img src = 'static/noimglow.png' loading='lazy'><br>\n"
                    img_data += "</a>"


        return render_template("collection.html", imgs = img_data)

#----------------------------------------------------------

@app.route("/setlist")
def setlist():
    set_files = os.listdir("data")
    set_files.sort()
    set_info = ""
    for set_name in set_files:
        file = open(f"data/{set_name}", "r")
        set = json.load(file)
        set_info += "<div class = 'flex'>"
        if "logo" in set:
            set_info += "<div class='w-[50px] h-[50px]'>"
            set_info += f"<img src = '{set['logo']}' class = 'object-scale-down'>"
            set_info += "</div>"
        set_info += f"<a href = '/displayset?SET={set['id']}'>{set['name']}</a><br>"
        set_info += "</div>"
    return render_template("sets.html", sets = set_info)

#----------------------------------------------------------

@app.route("/card/<string:card_id>", methods=["POST","GET"])
def get_card_info(card_id):

    user_id = user.get_user_id(session["username"])
    user_cards = user.get_cards(user_id)
    deck = user.get_deck(user_id)

    user_owns = "false"
    in_deck = "false"
    if user_cards != -1:
        if card_id in user_cards:
            user_owns = "true"
        if deck != -1:
            if card_id in deck:
                in_deck = "true"

    info_arr = card_id.split("-")
    set_id = ""
    local_id = info_arr[-1]


    for i in info_arr:
        if i != local_id:
            set_id += f"{i}-"
    set_id = set_id[:-1]
    if("SWSH" in local_id):
        local_id = local_id[4:]
    if("BW" in local_id or "XY" in local_id or "SM" in local_id):
        local_id = local_id[2:]
    local_id = str(card.correct_card_id_backwards(int(local_id), set_id))


    if(set_id == "svp" and local_id == "221"):
        local_id = "220"

    file = open(f"data/{set_id}.json", "r")
    print(local_id)
    data = json.load(file)["cards"][int(local_id)]
#    print(data)

    img_data = ""
    if 'image' in data:
        img_data += f"<a href = '{data['image']}/high.png' target = _blank>\n"
        img_data += f"<img src = '{data['image']}/high.png'><br>\n"
        img_data += "</a>"
    else:
        img_data += f"<img src = '../static/noimghigh.png'><br>\n"
        img_data += "</a>"

    card_info = ""
    card_info += f"Name: {data['name']}<br>\n"
    card_info += f"Category: {data['category']}<br>\n"
    if(data["category"] == "Trainer"):
        if "trainerType" in data:
            card_info += f"Trainer Type: {data['trainerType']}<br>\n"
        if "effect" in data:
            card_info += f"Effect: {data['effect']}<br>\n"
    if(data["category"] == "Pokemon"):
        if "types" in data:
            card_info += f"Type: {data['types'][0]}<br>\n"
        if "hp" in data:
            card_info += f"HP: {data['hp']}<br>\n"
        if "evolveFrom" in data:
            card_info += f"Evolves From: {data['evolveFrom']}<br>\n"
        if "abilities" in data:
            card_info += f"Abilities:<br>\n"
            card_info += card.abilities_to_str(data['abilities'])
        if "attacks" in data:
            card_info += "Attacks:<br>\n"
            card_info += card.attacks_to_str(data['attacks'])
        if "weaknesses" in data:
            card_info += f"Weaknesses:<br>\n"
            card_info += card.weaknesses_to_str(data['weaknesses'])
        if "retreat" in data:
            card_info += f"Retreat Cost: {data['retreat']}<br>\n"


    return render_template("card.html", in_deck = in_deck, card_id = card_id, owned = user_owns, card_img = img_data, card_data = card_info)



#----------------------------------------------------------

@app.route("/login.html")
def loginhtml():
    if 'username' in session:
        return redirect("/")
    return render_template("login.html")

#----------------------------------------------------------

@app.route("/register.html")
def registerhtml():
    if 'username' in session:
        return redirect("/")
    return render_template("register.html")

#----------------------------------------------------------

@app.route("/register", methods = ["POST", "GET"])
def register():
    if('username' in session): # If not coming from login page or if already logged in
        return redirect("/")

    userName = request.form['username']
    temp = ""
    for i in userName:
        if i != '"':
            temp += i
    userName = temp
    if(len(userName) < 1):
        return render_template("register.html", username_error = "Please enter a valid username")

    USER_DB = sqlite3.connect(DB_NAME)
    USER_DB_CURSOR = USER_DB.cursor()

    USER_DB_CURSOR.execute(f"SELECT COUNT(*) FROM userdata WHERE username = ?;",(userName,))
    alreadyExists = USER_DB_CURSOR.fetchone()[0]
    if(alreadyExists != 0):
        return render_template("register.html", username_error = "Username already taken")


    USER_DB_CURSOR.execute("INSERT INTO userdata VALUES(?,?, NULL, NULL, NULL);",(userName,request.form["password"],))
    session['username'] = userName

    USER_DB.commit()
    USER_DB.close()
    return redirect("/")

#----------------------------------------------------------

@app.route("/login", methods = ["POST", "GET"])
def login():
    if('username' in session): # If not coming from login page or if already logged in
        return redirect("/")
    USER_DB = sqlite3.connect(DB_NAME)
    USER_DB_CURSOR = USER_DB.cursor()

    userName = request.form['username']
    USER_DB_CURSOR.execute(f"SELECT COUNT(*) FROM userdata WHERE username = ?;",(userName,))
    alreadyExists = USER_DB_CURSOR.fetchone()[0]
    if(alreadyExists == 0):
        return render_template("login.html", username_error = "User does not exist")
    USER_DB_CURSOR.execute(f"SELECT password FROM userdata WHERE username = ?;",(userName,))
    userPass = USER_DB_CURSOR.fetchone()[0]
    if(not userPass == request.form["password"]):
        return render_template("login.html", password_error = "Password is incorrect")
    session["username"] = request.form["username"]

    USER_DB.commit()
    USER_DB.close()

    return redirect("/")

#----------------------------------------------------------

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login.html")


app.debug = True
app.run()
