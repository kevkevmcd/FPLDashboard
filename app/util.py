from premier_league_api import(
    get_static_elements_response,
    get_element_status_response,
    get_details_response,
    get_transactions_response,
    get_choices_response
)

# Returns the name of the premier league team given a team id.
def get_team_from_id(id):
    for i in get_static_elements_response().json()["teams"]:
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
    for i in get_element_status_response().json()["element_status"]:
        if player_id == i["element"]:
            return i["owner"]
    return owner


# Returns the player's web name given the player id.
def get_player_web_name(id):
    for i in get_static_elements():
        if id == i["id"]:
            return i["web_name"]
        
        
def get_player_code(id):
    for i in get_static_elements():
        if id == i["id"]:
            return i["code"]


def get_player_id(player_name):
    if player_name is None:
        return None
    
    player_name_lower = player_name.lower()
    for i in get_static_elements():
        if match_player_name(player_name_lower, i):
            return i["id"]


# Returns the full manager name given the manager id.
def get_manager_name(id):
    for i in get_league_entries():
        if id == i["entry_id"]:
            return ", " + i["player_first_name"] + " " + i["player_last_name"]
    return ""


# Returns the manager's team name given the manager id.
def get_manager_team_name(id):
    for i in get_league_entries():
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

#player squad methods
def get_manager_squad(manager_id):
    response = get_element_status_response().json()["element_status"]
    squad = []

    for element in response:
        if element["owner"] == manager_id:
            player = element["element"]
            squad.append(player)

    return squad

def match_team_name(team_name_input, entries):
    if (team_name_input == entries["entry_name"].lower()):
        return True
    return False

    
#Specific data from responses
def get_matches():
    response = get_details_response().json()
    matches = response["matches"]

    return matches

def get_league_entries():
    response = get_details_response().json()
    leagueEntries = response["league_entries"]

    return leagueEntries

def get_standings():
    response = get_details_response().json()
    standings = response["standings"]

    return standings

def get_transactions():
    response = get_transactions_response().json()
    transactions = response["transactions"]

    return transactions

def get_choices():
    response = get_choices_response().json()
    choices = response["choices"]

    return choices

def get_league():
    response = get_details_response().json()
    league = response["league"]

    return league

def get_static_elements():
    response = get_static_elements_response().json()
    elements = response["elements"]
    
    return elements

def get_teams():
    response = get_static_elements_response().json()
    teams = response["teams"]

    return teams

#Other commonly used methods
def get_columns():
    columns = []
    league_entries = get_league_entries()

    for entry in league_entries:
        columns.append(entry["id"])
    
    return columns

def get_entry_names():
    entry_names = {}
    league_entries = get_league_entries()

    for entry in league_entries:
        entry_id = entry["id"]
        entry_name = entry["entry_name"]
        entry_names[entry_id] = entry_name
    
    return entry_names

def get_team_name(team_id):
    team_name = ""
    teams = get_teams()

    for team in teams:
        if team["id"] == team_id:
            team_name = team["name"]

    return team_name

def get_league_team_names():
    entries = get_league_entries()
    teams = []
    team = ""

    for entry in entries:
        team = entry["entry_name"]
        teams.append(team)
    
    return teams


def get_manager_team_name_for_fixtures(id):
    for i in get_league_entries():
        if id == i["id"]:
            return i["entry_name"] + " - " + i["short_name"]
    return "Unknown"

def style_results(val):
    style = {
        'W': 'background-color: green; color: white;',
        'L': 'background-color: red; color: white;',
        'D': 'background-color: gray; color: white;'
    }
    return style.get(val, '') + 'text-align: center;'
    
            