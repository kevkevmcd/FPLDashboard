import pandas as pd
from util import(
    get_league_entries,
    match_team_name,
    get_static_elements,
    get_manager_squad
)

def get_manager_id(manager_name):
    entries = get_league_entries()
    manager_id = 0

    for entry in entries:
        if entry["entry_name"] == manager_name:
            manager_id = entry["entry_id"]
    
    return manager_id

def get_team_name(team_name):
    team_name_lower = team_name.lower()
    for i in get_league_entries():
        if match_team_name(team_name_lower, i):
            return i["entry_name"]
    return ""

def get_player_totals(player_id):
    elements = get_static_elements()
    df = pd.DataFrame()

    name = []
    #team_name = ""
    total_points = []
    minutes = []
    goals_scored = []
    assists = []
    clean_sheets = []
    points_per_game = []
    form = []
    bps = []
    influence = []
    creativity = []
    threat = []

    for element in elements:
        if element["id"] == player_id:
            name.append(element["first_name"] + " " + element["second_name"])
            total_points.append(element["total_points"])
            minutes.append(element["minutes"])
            goals_scored.append(element["goals_scored"])
            assists.append(element["assists"])
            clean_sheets.append(element["clean_sheets"])
            points_per_game.append(element["points_per_game"])
            form.append(element["form"])
            bps.append(element["bps"])
            influence.append(element["influence"])
            creativity.append(element["creativity"])
            threat.append(element["threat"])
    
    df["Name"] = name
    df["Total Points"] = total_points
    df["minutes"] = minutes
    df["GS"] = goals_scored
    df["Assists"] = assists
    df["CS"] = clean_sheets
    df["PPG"] = points_per_game
    df["Form"] = form
    df["BPS"] = bps
    df["Influence"] = influence
    df["Creativity"] = creativity
    df["Threat"] = threat
    
    return df

def get_squad_info(manager_id):
    df = pd.DataFrame()
    if manager_id == 0:
        return df

    squad = get_manager_squad(manager_id)

    for player in squad:
        player_info = get_player_totals(player)
        df = pd.concat([df, player_info], ignore_index=True).sort_values(by="Total Points", ascending=False)

    return df

#This is just temporary, I will get rid of this when I don't feel like being lazy
def get_manager_name_without_comma(id):
    for i in get_league_entries():
        if id == i["entry_id"]:
            return i["player_first_name"] + " " + i["player_last_name"]
    return ""