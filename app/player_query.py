import pandas as pd
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError
from util import(
    get_static_elements,
    match_player_name,
    get_team_from_id,
    get_player_position,
    get_player_id,
    get_player_owner,
    get_manager_team_name,
    get_manager_name,
    get_player_code
)
from premier_league_api import(
    get_player_picture
)


# Returns the full name of the player name provided. Returns an empty string if the player cannot be found.
# TODO: Add proper error handling.
def get_player_name(player_name):
    player_name_lower = player_name.lower()
    # TODO(mgribbins567): Add handling for player's with annoying letters, and searching using non-web_name (first/last/nickname).
    # TODO(mgribbins567): Stretch goal: add best-guess search for misspellings etc.
    for i in get_static_elements():
        if match_player_name(player_name_lower, i):
            return i["first_name"] + " " + i["second_name"]
    return ""


# Returns the Team and Position of the player name provided.
def get_player_info(player_name):
    # TODO: Might want to call get_player_name or another util to use ID based matching once we implement better searching.
    player_name_lower = player_name.lower()
    for i in get_static_elements():
        if match_player_name(player_name_lower, i):
            player_position = i["element_type"]
            player_team = i["team"]
            break
    return (
        get_team_from_id(player_team)
        + " "
        + get_player_position(player_position)
    )


# Returns the manager team name and manager name for the player provided.
def get_owner_info(player_name):
    player_id = get_player_id(player_name)
    owner_id = get_player_owner(player_id)
    return get_manager_team_name(owner_id) + get_manager_name(owner_id)


# Returns a DataFrame for the player's history.
# TODO: Add future fixture list.
def get_player_history(player_name):
    # If there is no player provided, just return an empty DataFrame.
    df = pd.DataFrame()
    if player_name == "":
        return df

    try:
        week = []
        opponent = []
        home_away = []
        minutes = []
        points = []
        goals = []
        assists = []
        clean_sheets = []
        goals_conceded = []
        yellows = []
        reds = []
        saves = []
        bonus = []
        bps = []

        player_id = get_player_id(player_name)
        if player_id is None:
            # Handle the case when player_id is not found
            return df

        player_summary = requests.get(
            f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        )

        # Raise an HTTPError for bad responses (4xx and 5xx status codes)
        player_summary.raise_for_status()

        for i in player_summary.json()["history"]:
            week.append(i["round"])
            opponent.append(get_team_from_id(i["opponent_team"]))
            if i["was_home"]:
                home_away.append("H")
            else:
                home_away.append("A")
            minutes.append(i["minutes"])
            points.append(i["total_points"])
            goals.append(i["goals_scored"])
            assists.append(i["assists"])
            clean_sheets.append(i["clean_sheets"])
            goals_conceded.append(i["goals_conceded"])
            yellows.append(i["yellow_cards"])
            reds.append(i["red_cards"])
            saves.append(i["saves"])
            bonus.append(i["bonus"])
            bps.append(i["bps"])

        # Append with totals.
        week.append("")
        opponent.append("")
        home_away.append("")
        minutes.append(sum(minutes))
        points.append(sum(points))
        goals.append(sum(goals))
        assists.append(sum(assists))
        clean_sheets.append(sum(clean_sheets))
        goals_conceded.append(sum(goals_conceded))
        yellows.append(sum(yellows))
        reds.append(sum(reds))
        saves.append(sum(saves))
        bonus.append(sum(bonus))
        bps.append(sum(bps))

        df["Gameweek"] = week
        df["Opponent"] = opponent
        df[""] = home_away
        df["Minutes"] = minutes
        df["Points"] = points
        df["Goals"] = goals
        df["Assists"] = assists
        df["CS"] = clean_sheets
        df["GC"] = goals_conceded
        df["Yellows"] = yellows
        df["Reds"] = reds
        df["Saves"] = saves
        df["Bonus"] = bonus
        df["Bps"] = bps

        return df

    except HTTPError as http_err:
        # Handle HTTP errors (4xx and 5xx)
        print(f"HTTP error occurred: {http_err}")
    except ConnectionError as conn_err:
        # Handle connection errors
        print(f"Connection error occurred: {conn_err}")
    except RequestException as req_err:
        # Handle other request errors
        print(f"Request error occurred: {req_err}")

    # Return an empty DataFrame if an error occurs
    return df


def get_picture(player_name):
    player_id = get_player_id(player_name)
    player_code = get_player_code(player_id)

    player_picture_link = get_player_picture(player_code)

    return player_picture_link
