import app


# Returns the name of the premier league team given a team id.
def get_team_from_id(id):
    for i in app.static_elements.json()["teams"]:
        if id == i["id"]:
            return i["name"]


# Returns the position abbreviation given the position id integer.
def get_player_position(position_id):
    if position_id == 1:
        return "Goalkeeper"
    elif position_id == 2:
        return "Defender"
    elif position_id == 3:
        return "Midfielder"
    elif position_id == 4:
        return "Forward"


# Returns the manager id who owns the player id given.
def get_player_owner(player_id):
    owner = "nobody"
    for i in app.element_status.json()["element_status"]:
        if player_id == i["element"]:
            return i["owner"]
    return owner


# Returns the player's web name given the player id.
def get_player_web_name(id):
    for i in app.static_elements.json()["elements"]:
        if id == i["id"]:
            return i["web_name"]


def get_player_id(player_name):
    player_name_lower = player_name.lower()
    for i in app.static_elements.json()["elements"]:
        if match_player_name(player_name_lower, i):
            return i["id"]


# Returns the full manager name given the manager id.
def get_manager_name(id):
    for i in app.league_details.json()["league_entries"]:
        if id == i["entry_id"]:
            return ", " + i["player_first_name"] + " " + i["player_last_name"]
    return ""


# Returns the manager's team name given the manager id.
def get_manager_team_name(id):
    for i in app.league_details.json()["league_entries"]:
        if id == i["entry_id"]:
            return i["entry_name"]
    return "Unowned"


def match_player_name(player_name_input, elements):
    if (
        player_name_input == elements["web_name"].lower()
        or player_name_input == elements["first_name"].lower()
        or player_name_input == elements["second_name"].lower()
        or player_name_input
        == (elements["first_name"].lower() + " " + elements["second_name"].lower())
    ):
        return True
    return False
