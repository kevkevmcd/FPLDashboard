import pandas as pd
import util
import requests


# Returns the full name of the player name provided. Returns an empty string if the player cannot be found.
# TODO: Add proper error handling.
def get_player_name(player_name):
    player_name_lower = player_name.lower()
    # TODO(mgribbins567): Add handling for player's with annoying letters, and searching using non-web_name (first/last/nickname).
    # TODO(mgribbins567): Stretch goal: add best-guess search for misspellings etc.
    for i in util.get_static_elements():
        if util.match_player_name(player_name_lower, i):
            return i["first_name"] + " " + i["second_name"]
    return ""


# Returns the Team and Position of the player name provided.
def get_player_info(player_name):
    # TODO: Might want to call get_player_name or another util to use ID based matching once we implement better searching.
    player_name_lower = player_name.lower()
    for i in util.get_static_elements():
        if util.match_player_name(player_name_lower, i):
            player_position = i["element_type"]
            player_team = i["team"]
            break
    return (
        util.get_team_from_id(player_team)
        + " "
        + util.get_player_position(player_position)
    )


# Returns the manager team name and manager name for the player provided.
def get_owner_info(player_name):
    player_id = util.get_player_id(player_name)
    owner_id = util.get_player_owner(player_id)
    return util.get_manager_team_name(owner_id) + util.get_manager_name(owner_id)


# Returns a DataFrame for the player's history.
# TODO: Add future fixture list.
def get_player_history(player_name):
    # If there is no player provided, just return an empty DataFrame.
    df = pd.DataFrame()
    if player_name == "":
        return df

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
    player_id = util.get_player_id(player_name)
    player_summary = requests.get(
        f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    )
    for i in player_summary.json()["history"]:
        week.append(i["round"])
        opponent.append(util.get_team_from_id(i["opponent_team"]))
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


def get_picture(player_name):
    player_id = util.get_player_id(player_name)
    player_code = util.get_player_code(player_id)

    player_picture_link = util.get_player_picture(player_code)

    return player_picture_link
