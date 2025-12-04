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

DB_NAME = "database.db"
DB = sqlite3.connect(DB_NAME)
DB_CURSOR = DB.cursor()

DB_CURSOR.execute("CREATE TABLE IF NOT EXISTS userdata(username TEXT, password TEXT, cards TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT);")

app = Flask(__name__)

app.secret_key = "83ut83ojreoikdlshg3958u4wjtse09gol.hi"

@app.route("/profile")
def homepage():
    if 'username' not in session:
        return render_template("login.html")

    if(not user.user_exists(session['username'])):
        return redirect("/logout")

    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()

    DB_CURSOR.execute(f"SELECT id FROM userdata WHERE username =\"{session['username']}\";")
    userId = DB_CURSOR.fetchone()[0]
    session['userId'] = userId
    numBlogs = blog.get_num_blogs(userId)
    arr = blog.get_blog_links(userId)
    return render_template("userprofile.html", username = session["username"], numblogs = numBlogs, blogs = blog.get_blogs(userId), txt = arr, owner = "true")

#----------------------------------------------------------

@app.route("/")
def homepagehtml():
    loggedIn = "false"
    if 'username' in session:
        user_id = user.get_user_id(session['username'])
        cards = user.get_cards(user_id)
        return render_template("homepage.html", test = cards)
    else:
        return redirect("/login.html")
    return render_template("homepage.html",logged_in = loggedIn)

#----------------------------------------------------------

@app.route("/addcard", methods = ["POST", "GET"])
def addcard():
    if 'username' in session:
        user_id = user.get_user_id(session['username'])
        user.add_card(user_id,request.args['TEST'])
        return redirect("/")
    return redirect("/")

@app.route("/displayset", methods=["POST","GET"])
def displayset():
    if("SET" not in request.args):
        return redirect("/")
    set_id = request.args["SET"]
    if os.path.exists(f"Data/{set_id}.json"):
        file = open(f"Data/{set_id}.json", "r")
        data = json.load(file)
    else:
        return redirect(f"/cache?SET={set_id}")
    set_data = data
    data = data["cards"]
    title_data = ""
    title_data += f"{set_data['name']}"
    if "logo" in set_data:
        title_data += f"<img class='h-[38px] w-[38px]'src = {set_data['logo']}><br><br>"
    img_data = ""
    for card in data:
        if(not type(card) is int):
            if "image" in card:
            # img_data += f"<a href='{card["image"]}/high.png' target = _blank>"
                img_data += f"<a href='card/{card['id']}'>"
                img_data += f"<img src = '{card['image']}/low.png'><br>\n"
                img_data += "</a>"
            else:
                img_data += f"<a href='card/{card['id']}'>"
                img_data += f"<img src = 'static/noimglow.png'><br>\n"
                img_data += "</a>"

    return render_template("collection.html", imgs = img_data)

#----------------------------------------------------------



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

    USER_DB_CURSOR.execute(f"SELECT COUNT(*) FROM userdata WHERE username = '{userName}';")
    alreadyExists = USER_DB_CURSOR.fetchone()[0]
    if(alreadyExists != 0):
        return render_template("register.html", username_error = "Username already taken")


    INSERT_STRING = f"INSERT INTO userdata VALUES('{userName}','{request.form['password']}', 'testcard', NULL);"
    USER_DB_CURSOR.execute(INSERT_STRING)
    print(request.form['username'] + ", " + request.form['password'] + ", " + INSERT_STRING)
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

    USER_DB_CURSOR.execute(f"SELECT COUNT(*) FROM userdata WHERE username = '{request.form['username']}';")
    alreadyExists = USER_DB_CURSOR.fetchone()[0]
    if(alreadyExists == 0):
        return render_template("login.html", username_error = "User does not exist")
    USER_DB_CURSOR.execute(f"SELECT password FROM userdata WHERE username = '{request.form['username']}';")
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
