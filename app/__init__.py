from flask import *
import urllib, os, json, sqlite3, random
import user, card

DB_NAME = "database.db"
DB = sqlite3.connect(DB_NAME)
DB_CURSOR = DB.cursor()

DB_CURSOR.execute("CREATE TABLE IF NOT EXISTS userdata(username TEXT, password TEXT, cards TEXT, deck TEXT, currency INT, id INTEGER PRIMARY KEY AUTOINCREMENT);")

app = Flask(__name__)
app.secret_key = "83ut83ojreoikdlshg3958u4wjtse09gol.hi"
#

@app.before_request
def before_request():
    # print(request.endpoint)
    pages = ['login', 'register', 'loginhtml', 'registerhtml', 'homepagehtml', 'login.html', 'register.html']
    if request.endpoint not in pages:
        if 'username' not in session or user.get_user_id(session['username']) == -1:
            session.pop("username", None)
            return redirect("/login.html")

#----------------------------------------------------------

@app.route("/search")
def search():
    currency = user.get_currency(user.get_user_id(session['username']))
    user_searched = request.args["username"]
    if user_searched == "":
        user_searched = "%"
    user_list = user.find_user(user_searched)
    if len(user_list) == 0:
        return redirect("/")
    text = ""

    for each_user in user_list:
        user_name = each_user[0]
        user_id = each_user[5]
        text += f"<a href='/displaycollection?id={user_id}'>{user_name}</a><br>\n"
    return render_template("search.html", search_list = text, currency = currency)

#----------------------------------------------------------

@app.route("/")
def homepagehtml():
    loggedIn = "false"
    if 'username' in session:
        if user.get_user_id(session['username']) == -1:
            return redirect("/login.html")
        user_id = user.get_user_id(session['username'])
        cards = user.get_cards(user_id)
        currency = user.get_currency(user_id)

        return render_template("homepage.html", currency = currency, test = cards)
    else:
        return redirect("/login.html")


    return render_template("homepage.html",logged_in = loggedIn)

#----------------------------------------------------------

@app.route("/trivia", methods = ["POST", "GET"])
def trivia():

    stat_types = ["hp", "attack", "defense", "special attack", "special defense", "speed"]
    types = ["fire", "water", "grass", "electric", "ghost", "poison", "ice", "dragon", "bug", "normal", "fighting", "flying", "ground", "rock", "psychic", "dark", "steel", "fairy"]
    user_id = user.get_user_id(session["username"])

    # print("type" in request.form)
    base_link = "https://pokeapi.co/api/v2/pokemon/"
    dex_num = random.randint(1,1025)
    json_data = urllib.request.urlopen(f"{base_link}{dex_num}")
    json_string = json_data.read()
    data = json.loads(json_string)
    gif_link = ""
    print(dex_num)

    if "type" in request.form:
        prev_dex_num = int(request.form["dexnum"])

        prev_json_data = urllib.request.urlopen(f"{base_link}{prev_dex_num}")
        prev_json_string = prev_json_data.read()
        prev_data = json.loads(prev_json_string)



        emotion = ""
        match request.form["type"]:
            case "gen":
                generation_cutoffs = [151, 251, 386, 493, 649, 721, 809, 905, 1025]
                for i in range(len(generation_cutoffs)):
                    if prev_dex_num <= generation_cutoffs[i]:
                        gen = i+1
                        break;
                if gen == int(request.form["question"]):
                    user.add_currency(user_id,10);
                    emotion = "happy"
                else:
                    emotion = "sad"

            case "height":
                # print(prev_data["height"] / 10)
                if request.form["question"] == str(prev_data["height"] / 10):
                    user.add_currency(user_id, 50)
                    emotion = "happy"
                else:
                    emotion = "sad"
            case "stats":
                correct_stat = prev_data["stats"][int(request.form["stattype"])]["base_stat"]
                # for i in request.form:
                #     print(i)
                if int(request.form["question"]) == correct_stat:
                    print("hooray!")
                    user.add_currency(user_id,100)
                    emotion = "happy"
                else:
                    emotion = "sad"
            case "type":
                correct_types = []
                for type in prev_data["types"]:
                    correct_types.append(type["type"]["name"])
                if len(correct_types) == 1:
                    correct_types.append(correct_types[0])
                type_string = "/".join(correct_types)
                reversed_correct_types = correct_types[::-1]
                reversed_type_string = "/".join(reversed_correct_types)
                if request.form["question"] == type_string or request.form["question"] == reversed_type_string:
                    print("yippee!")
                    user.add_currency(user_id,30)
                    emotion = "happy"
                else:
                    emotion = "sad"
            case "weight":
                # print(prev_data["height"] / 10)
                if request.form["question"] == str(prev_data["weight"] / 10):
                    user.add_currency(user_id, 50)
                    emotion = "happy"
                else:
                    emotion = "sad"

        if "type" in request.form:
            print("hi")
            file = open("keys/key_giphy.txt")
            api_key = file.read()
            api_key = api_key.strip()
            rand_offset = 1 #random.randint(0,4999)

            base_giphy_link = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&limit=1&q={emotion}"

            giphy_data = json.loads(urllib.request.urlopen(base_giphy_link).read())
            gif_link = f"<img src='{giphy_data['data'][0]['images']['original']['url']}'>"
            # check = 0
            # while(check == 0):
            #
            #     if len(giphy_data['data']) > 0:
            #
            #         check = 1
            #     else:
            #         check = 0
            #         rand_offset = random.randint(0,4999)

    currency = user.get_currency(user_id)

    img_str = ""
    if data['sprites']['back_default'] != None:
        img_str += f"<img src ='{data['sprites']['back_default']}'><br>\n"
    img_str += f"<img src ='{data['sprites']['front_default']}'><br>\n"

    possible_topics = ["gen","height","stats","type","weight"]
    topic = random.choice(possible_topics)

    stat_type = ""
    # topic = "gen"
    question_type = ""
    match topic:
        case "gen":
            question_type = "generation"
            generation_cutoffs = [151, 251, 386, 493, 649, 721, 809, 905, 1025]
            for i in range(len(generation_cutoffs)):
                if dex_num <= generation_cutoffs[i]:
                    gen = i+1
                    break;
            match gen:
                case 1:
                    possible_answers = [gen, gen + 1, gen + 2, gen + 3]
                case 8:
                    possible_answers = [gen, gen + 1, gen - 1, gen - 2]
                case 9:
                    possible_answers = [gen, gen - 1, gen - 2, gen - 3]
                case _:
                    possible_answers = [gen, gen + 1, gen - 1, gen + 2]

        case "height":
            question_type = "height (in meters)"
            real_height = int(data['height']) / 10.0
            format(real_height, '0.2f')
            possible_answers = []
            possible_answers.append(real_height)
            for i in range (0,3):
                rand_modifier = random.randint(65,85) / 100
                if random.randint(0,101294102129313) % 2 == 0:
                    rand_modifier = random.randint(115, 135) / 100
                possible_answers.append(round(real_height * rand_modifier, 2))

        case "stats":
            specific_stat = random.randint(0,5)
            stat_type = specific_stat
            correct_stat = int(data['stats'][specific_stat]["base_stat"])
            question_type = f"{stat_types[stat_type]} stat"
            print(stat_type)
            print(correct_stat)
            possible_answers = []
            possible_answers.append(correct_stat)
            for i in range (0,3):
                rand_modifier = random.randint(65,85) / 100
                if random.randint(0,101294102129313) % 2 == 0:
                    rand_modifier = random.randint(115, 135) / 100
                temp_stat = round(correct_stat * rand_modifier)
                if temp_stat == correct_stat:
                    temp_stat += random.randint(0,340343) % 4
                possible_answers.append(temp_stat)


        case "type":
            question_type = "type"
            correct_types = []
            for type in data["types"]:
                correct_types.append(type["type"]["name"])
            if len(correct_types) == 1:
                correct_types.append(correct_types[0])
            type_string = "/".join(correct_types)
            possible_answers = []
            possible_answers.append(type_string)
            for i in range(0,3):
                possible_typing = []
                type1 = random.choice(types)
                type2 = random.choice(types)
                type_check = random.randint(0,10230123123) % 2
                if type1 not in correct_types:
                    if random.randint(0,120124124123) % 5 > 2:
                        type1 = correct_types[type_check]
                if type2 not in correct_types:
                    if random.randint(0,120124124123) % 5 > 2:
                        type2 = correct_types[type_check]
                possible_typing.append(type1)
                possible_typing.append(type2)
                possible_typing_string = "/".join(possible_typing)

                other_possible_typing = possible_typing[::-1]

                other_possible_typing_string = "/".join(other_possible_typing)
                if possible_typing_string == type_string or other_possible_typing_string == type_string:
                    while(type1 == correct_types[0] or type1 == correct_types[1]):
                        type1 = random.choice(types)
                    possible_typing[0] = type1
                    possible_typing[1] = type2
                    # print(possible_typing)
                    possible_typing_string = "/".join(possible_typing)

                possible_answers.append(possible_typing_string)

        case "weight":
            question_type = "weight (in kg)"
            real_weight = int(data['weight']) / 10.0
            format(real_weight, '0.2f')
            possible_answers = []
            possible_answers.append(real_weight)
            for i in range (0,3):
                rand_modifier = random.randint(65,85) / 100
                if random.randint(0,101294102129313) % 2 == 0:
                    rand_modifier = random.randint(115, 135) / 100
                possible_answers.append(round(real_weight * rand_modifier, 2))

    random.shuffle(possible_answers)
    return render_template("testing.html", currency = currency, testimg = img_str, gif = gif_link, question_type = question_type, stattype = stat_type, dexnum = dex_num, type = topic, q1 = possible_answers[0], q2 = possible_answers[1], q3 = possible_answers[2], q4 = possible_answers[3])


#----------------------------------------------------------

@app.route("/pullhtml", methods=["POST","GET"])
def pullhtml():
    user_id = user.get_user_id(session["username"])
    currency = user.get_currency(user_id)
    return render_template("pull.html", currency = currency, pull_error = -1)

#----------------------------------------------------------

@app.route("/pull", methods = ["POST", "GET"])
def pull():
    if 'username' in session:
        if 'count' in request.args:
            num_pulls = int(request.args['count'])
        else:
            num_pulls = 1
        user_id = user.get_user_id(session['username'])
        currency = user.get_currency(user_id)

        pull_cost = 150
        pull_cost -= int(num_pulls / 10) * 50
        if(currency >= num_pulls * pull_cost):
            user.add_currency(user_id,-(num_pulls * pull_cost))
        else:
            if "set" in request.args:
                return redirect(f"/displayset?SET={request.args['set']}")
            return render_template("pull.html", currency = currency, pull_error = "You don't have enough currency")
        currency = user.get_currency(user_id)
        cards = ""
        cards_without_images = 0

        for i in range (num_pulls):
            random_card = -1
            while isinstance(random_card, int):
                if "set" not in request.args:
                    random_set = random.choice(os.listdir("data"))
                    random_set = random_set[:-5]
                else:
                    random_set = request.args['set']


                file = open(f"data/{random_set}.json", "r")
                data = json.load(file)["cards"]
                # print(data)
                random_card = random.choice(data)
                if not isinstance(random_card, int):
                    if not "image" in random_card:
                        random_card = -1

            if "image" in random_card:
                random_card_id = random_card["id"]
                cards += f"<a href='/card/{random_card_id}'>\n"
                cards += f"<img src='{random_card['image']}/low.jpg'>\n"
                cards += "</a>\n"
                print(random_card["rarity"])
                user.add_card(user_id,random_card_id)

        if "set" in request.args:
            return redirect(f"/displayset?SET={request.args['set']}")
        # print(cards)
        return render_template("pull.html", cards_pulled = cards, pull_error = -1, currency = currency)
    return redirect("/")

#----------------------------------------------------------

@app.route("/removecards", methods=["POST","GET"])
def remove_cards():
    user.remove_cards(user.get_user_id(session["username"]))
    return redirect("/")

#----------------------------------------------------------


@app.route("/remove_deck", methods=["POST","GET"])
def remove_from_deck():
    user_id = user.get_user_id(session["username"])
    user.remove_card_from_deck(user_id, request.args["id"])
    return redirect(f"/displaycollection")

#----------------------------------------------------------

@app.route("/add_deck", methods=["POST","GET"])
def add_to_deck():
    if "id" not in request.args:
        return redirect("/")

    card_id = request.args["id"]
    user_id = user.get_user_id(session["username"])
    user.add_card_to_deck(user_id,card_id)
    return redirect(f"/displaycollection")


#----------------------------------------------------------

@app.route("/addcurrency", methods=["POST","GET"])
def add_currency():
    user_id = user.get_user_id(session["username"])
    user.add_currency(user_id,request.args["count"])
    return redirect(request.args["page"])
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

        is_set = "True"
        user_id = user.get_user_id(session['username'])
        currency = user.get_currency(user_id)
        user_cards = user.get_cards(user_id)
        set_data = data
        data = data["cards"]

        title_data = ""
        set_name = set_data['name']
        if "logo" in set_data:
            set_logo = set_data['logo']
        else:
            set_logo = ""

        img_data = ""
        for card in data:
            if not isinstance(card,int):
                grayscale = "grayscale"
                if not isinstance(user_cards, int):
                    if card['id'] in user_cards:
                        grayscale = "grayscale-0"
                if "image" in card:
                # img_data += f"<a href='{card["image"]}/high.jpg' target = _blank>"
                    img_data += f"<a href='card/{card['id']}'>"
                    img_data += f"<img src = '{card['image']}/low.jpg' loading='lazy' class='{grayscale}'><br>\n"
                    img_data += "</a>"
                # else:
                #     img_data += f"<a href='card/{card['id']}'>"
                #     img_data += f"<img src = 'static/noimglow.jpg' loading='lazy' ><br>\n"
                #     img_data += "</a>"
    else:
        return redirect("/")
    if img_data == "":
        return render_template("collection.html", is_set = is_set, set_id = set_id, set_name = set_name, set_logo = set_logo, deck = "Set has no images", cards = -1, currency = currency)
    return render_template("collection.html", is_set = is_set, set_id = set_id, set_name = set_name, set_logo = set_logo, deck = img_data, title = title_data, cards = -1, currency = currency)

#----------------------------------------------------------

@app.route("/displaycollection")
def display_collec():
    user_id = user.get_user_id(session['username'])
    currency = user.get_currency(user_id)
    if not "id" in request.args:
        card_info = display_collection("cards")
    else:
        card_info = -1
    deck_info = display_collection("deck")

    return render_template("collection.html", is_set = False, deck = deck_info, cards = card_info, currency = currency)

#----------------------------------------------------------

@app.route("/displaycollection/<string:type>")
def display_collection(type):
    if "username" in session:
        if not "id" in request.args:
            user_id = user.get_user_id(session["username"])
        else:
            user_id = request.args["id"]

        img_data = ""
        if type == "cards":
            cards_list = user.get_cards(user_id)
        if type == "deck":
            cards_list = user.get_deck(user_id)
        if isinstance(cards_list,int):
            # img_data = "You have no cards."
            return -1
            # return render_template("collection.html", imgs = img_data)
        for each_card in cards_list:
            if each_card != "":
                info_arr = each_card.split("-")
                set_id = ""
                local_id = info_arr[-1]

                for i in info_arr:
                    if i != local_id:
                        set_id += f"{i}-"
                set_id = set_id[:-1]
                if("SWSH" in local_id or "HGSS" in local_id):
                    local_id = local_id[4:]
                if("BW" in local_id or "XY" in local_id or "SM" in local_id or "SV" in local_id or "GG" in local_id or "DP" in local_id or "SH" in local_id or "RC" in local_id or "TG" in local_id or "SL" in local_id):
                    local_id = local_id[2:]
                local_id = str(card.correct_card_id_backwards(int(local_id), set_id))

                if os.path.exists(f"data/{set_id}.json"):
                    file = open(f"data/{set_id}.json", "r")
                    data = json.load(file)["cards"][int(local_id)]
                    if "image" in data:
                    # img_data += f"<a href='{card["image"]}/high.jpg' target = _blank>"
                        img_data += "<div class='object-center m-2'>"
                        img_data += f"<a href='/card/{data['id']}'>"
                        img_data += f"<img src = '{data['image']}/low.jpg' loading='lazy'><br>\n"
                        img_data += "</a>"
                        img_data += "</div>"
                    else:
                        img_data += "<div class ='object-center'>"
                        img_data += f"<a href='/card/{data['id']}'>"
                        img_data += f"<img src = 'static/noimglow.jpg' loading='lazy'><br>\n"
                        img_data += "</a>"
                        img_data += "</div>"

        return img_data

#----------------------------------------------------------

@app.route("/setlist")
def setlist():
    user_id = user.get_user_id(session["username"])
    currency = user.get_currency(user_id)
    set_files = os.listdir("data")
    set_files.sort()
    set_info = ""
    for set_name in set_files:
        file = open(f"data/{set_name}", "r")
        set = json.load(file)
        set_info += "<div class = 'flex'>"

        image_count = 0
        for card in set["cards"]:
            if not isinstance(card,int):
                if "image" in card:
                    image_count+= 1
        if "logo" in set and image_count > 0:
            set_info += "<div class='w-[100px] h-[100px] m-8'>\n"
            set_info+= f"<a href = '/displayset?SET={set['id']}'>"
            set_info += "<button class='w-[100px] h-[100px] rounded-full bg-blue-500 hover:bg-red-500 text-white pl-[10px] border-5 border-blue-700'>\n"
            set_info += f"<img src = '{set['logo']}' class = 'object-scale-down justify-center w-[70px] h-[70px]' loading='lazy'>\n"
            set_info += "</button>\n"
            set_info += "</a><br>\n"
            set_info += "</div>\n"
        else:
            set_info += ""
            #set_info += f"<a href = '/displayset?SET={set['id']}'>{set['name']}</a><br>"
        set_info += "</div>\n\n"
    return render_template("sets.html", sets = set_info, currency = currency)

#----------------------------------------------------------

@app.route("/card/<string:card_id>", methods=["POST","GET"])
def get_card_info(card_id):

    user_id = user.get_user_id(session["username"])
    currency = user.get_currency(user_id)
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
    if("SWSH" in local_id or "HGSS" in local_id):
        local_id = local_id[4:]
    if("BW" in local_id or "XY" in local_id or "SM" in local_id or "SV" in local_id or "GG" in local_id or "DP" in local_id or "SH" in local_id or "RC" in local_id or "TG" in local_id or "SL" in local_id):
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
        img_data = data['image']

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


    return render_template("card.html", currency = currency, in_deck = in_deck, card_id = card_id, owned = user_owns, card_img = img_data, card_data = card_info)




#----------------------------------------------------------

@app.route("/login.html")
def loginhtml():
    if 'username' in session:
        if user.get_user_id(session["username"]) != -1:
            return redirect("/")
    return render_template("login.html")

#----------------------------------------------------------

@app.route("/register.html")
def registerhtml():
    if 'username' in session:
        if user.get_user_id(session["username"]) != -1:
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
    if(len(request.form["password"]) < 1):
        return render_template("register.html", password_error = "Please enter a valid password")
    USER_DB = sqlite3.connect(DB_NAME)
    USER_DB_CURSOR = USER_DB.cursor()

    USER_DB_CURSOR.execute(f"SELECT COUNT(*) FROM userdata WHERE username = ?;",(userName,))
    alreadyExists = USER_DB_CURSOR.fetchone()[0]
    if(alreadyExists != 0):
        return render_template("register.html", username_error = "Username already taken")


    USER_DB_CURSOR.execute("INSERT INTO userdata VALUES(?,?, NULL, NULL, 0, NULL);",(userName,request.form["password"],))
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
