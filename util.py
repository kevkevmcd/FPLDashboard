import app
import requests

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

#This is just temporary, I will get rid of this when I don't feel like being lazy
def get_manager_name_without_comma(id):
    for i in get_league_entries():
        if id == i["entry_id"]:
            return i["player_first_name"] + " " + i["player_last_name"]
    return ""

def match_team_name(team_name_input, entries):
    if (team_name_input == entries["entry_name"].lower()):
        return True
    return False

def get_league_code():
    league_code = int(app.code)
    return league_code

#responses
def get_details_response():
    league_code = get_league_code()
    response = requests.get(
        f"https://draft.premierleague.com/api/league/{league_code}/details"
        )

    return response

def get_transactions_response():
    league_code = get_league_code()
    response = requests.get(
        f"https://draft.premierleague.com/api/draft/league/{league_code}/transactions"
        )

    return response

def get_choices_response():
    league_code = get_league_code()
    response = requests.get(
        f"https://draft.premierleague.com/api/draft/{league_code}/choices"
        )

    return response

def get_static_elements_response():
    response = requests.get(
        "https://fantasy.premierleague.com/api/bootstrap-static/"
        )

    return response

def get_this_weeks_fixtures_response(gameweek):
    response = requests.get(
        f"https://fantasy.premierleague.com/api/fixtures?event={gameweek}"
    )

    return response

def get_element_status_response():
    league_code = get_league_code()
    response = requests.get(
        f"https://draft.premierleague.com/api/league/{league_code}/element-status"
        )

    return response

def get_live_gameweek_response(gameweek):
    response = requests.get(f"https://draft.premierleague.com/api/event/{gameweek}/live")

    return response

def get_team_details_response(gameweek, team_id):
    response = requests.get(f"https://draft.premierleague.com/api/entry/{team_id}/event/{gameweek}")

    return response

def get_player_picture(code):
    url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png"

    return url

def get_club_picture(code):
    response = requests.get(f"https://resources.premierleague.com/premierleague/badges/{code}.png")

    return response

def get_current_event_response():
    response = requests.get("https://draft.premierleague.com/api/game")

    return response

def get_current_gameweek():
    response = get_current_event_response().json()
    current_event = response["current_event"]

    return current_event

def get_upcoming_gameweek():
    response = get_current_event_response().json()
    week = response["current_event"]

    if response["current_event_finished"] == True:
        upcoming_gameweek = response["next_event"]
        week = upcoming_gameweek
    
    return week
    
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

def get_league_name():
    league = get_league()
    league_name = league["name"]

    return league_name

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

def get_rows():
    row = []
    row = [x + 1 for x in range(get_current_gameweek())]

    return row

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

def make_team_name_link(team_name):
    return f'<form method="POST" action="/manager_search/{team_name}"><button type="submit" class="btn btn-link"><div class="input-group justify-content-center"><span class="input-group-text" id="basic-addon1"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg></span></div></button></form>'

def get_manager_team_name_for_fixtures(id):
    for i in get_league_entries():
        if id == i["id"]:
            return i["entry_name"]
    return "Unknown"

def style_results(val):
    style = ''
    if val == 'W':
        style = 'background-color: green; color: white;'
    elif val == 'L':
        style = 'background-color: red; color: white;'
    elif val == 'D':
        style = 'background-color: gray; color: white;'
    
    # Add centering style
    return f'{style} text-align: center;'