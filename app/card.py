def correct_card_id_backwards(i, set_id):
    if(set_id == "svp"):
        if (i == 224 or i == 225):
            i-= 5
        if (i == 500):
            i = 221
        if(i > 176):
            i-=2
    if(set_id == "swshp"):
        if(i > 293):
            i-=2
        if(i > 290):
            i-=4
        if(i > 284):
            i-=3
        if(i > 251):
            i-= 1
        if(i > 75):
            i-= 1
    return i

def attacks_to_str(attacks):
    return_str = ""
    for attack in attacks:
        if "name" in attack:
            return_str += f"Name: {attack['name']}<br>\n"
            if "effect" in attack:
                return_str += f"Effect: {attack['effect']}<br>\n"
            if "damage" in attack:
                return_str += f"Damage: {attack['damage']}<br>\n"
            if "cost" in attack:
                return_str+= "Cost:<br>\n"
                for c in attack["cost"]:
                    return_str += f"&nbsp;&nbsp;&nbsp;{c}<br>\n"
    return return_str

def abilities_to_str(abilities):
    return_str = ""
    for ability in abilities:
        return_str += f"Name: {ability['name']}<br>\n"
        return_str += f"Effect: {ability['effect']}<br>\n"
    return return_str


def weaknesses_to_str(weaknesses):
    return_str = ""
    for weakness in weaknesses:
        return_str += f"Type: {weakness['type']}<br>\n"
        return_str += f"Value: {weakness['value']}<br>\n"
    return return_str
