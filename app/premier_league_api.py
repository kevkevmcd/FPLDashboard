import requests
from code_helper import get_league_code

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