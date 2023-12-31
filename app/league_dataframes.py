import pandas as pd
import numpy as np
from util import(
    get_standings,
    get_transactions,
    get_league_entries,
    get_details_response,
    get_entry_names,
    get_columns,
    get_matches,
    style_results,
    get_choices,
    get_team_name,
    get_manager_team_name_for_fixtures,
    get_league,
)
from premier_league_api import(
    get_this_weeks_fixtures_response,
    get_current_event_response
)

# returns dataframe for player point differentials
def point_differential():
    entry_names = get_entry_names()
    standings = get_standings()

    team_diffs = {}
    for team in standings:
        team_name = entry_names[team["league_entry"]]
        points_for = team["points_for"]
        points_against = team["points_against"]
        diff = points_for - points_against
        team_diffs[team_name] = diff

    df = pd.DataFrame.from_dict(
        team_diffs, orient="index", columns=["Point Difference"]
    )
    df = df.sort_values(by="Point Difference", ascending=False)
    df = df.reset_index()
    df = df.rename(columns={"index": "Team", "Point Difference": "Point Difference"})

    return df


# returns dataframe for each players transactions each week
def weekly_trades():
    transactions = get_transactions()
    league_entries = get_league_entries()

    teams = {entry["entry_id"]: entry["entry_name"] for entry in league_entries}
    columns = list(teams.values())
    gameweek = get_upcoming_gameweek()
    index = [x + 1 for x in range(gameweek)]
    df = pd.DataFrame(0, columns=columns, index=index)

    for transaction in transactions:
        event = transaction["event"]
        team_id = transaction["entry"]
        team_name = teams.get(team_id)
        result = transaction["result"]

        if team_name and result == "a":
            df.at[event, team_name] += 1

    return df


# returns dataframe for each players total amount of points scored per week
def weekly_total_points():
    response = get_details_response().json()
    entry_names = get_entry_names()
    columns = get_columns()
    gameweek = get_upcoming_gameweek()
    row = [x + 1 for x in range(gameweek)]
    matches = get_matches()

    new_columns = [entry_names[x] for x in columns]
    df = pd.DataFrame(response, columns=new_columns, index=row)

    for match in matches:
        event = match["event"]
        if event > gameweek:
            break

        league_entry_1 = match["league_entry_1"]
        league_entry_1_points = match["league_entry_1_points"]
        league_entry_2 = match["league_entry_2"]
        league_entry_2_points = match["league_entry_2_points"]

        df.at[event, entry_names[league_entry_1]] = league_entry_1_points
        df.at[event, entry_names[league_entry_2]] = league_entry_2_points

    return df


# returns dataframe for each players win/loss/draw points each week added to what they already had
def weekly_win_loss_points_cumsum():
    entry_names = get_entry_names()
    matches = get_matches()
    points_df = weekly_total_points().astype(float)

    for match in matches:
        event = match["event"]
        if match["finished"] == False:
            league_entry_1 = entry_names[match["league_entry_1"]]
            league_entry_2 = entry_names[match["league_entry_2"]]
            points_df.at[event, league_entry_1] = np.nan
            points_df.at[event, league_entry_2] = np.nan
            continue
        league_entry_1 = entry_names[match["league_entry_1"]]
        league_entry_1_points = match["league_entry_1_points"]
        league_entry_2 = entry_names[match["league_entry_2"]]
        league_entry_2_points = match["league_entry_2_points"]

        if league_entry_1_points > league_entry_2_points:
            points_df.at[event, league_entry_1] = 3
            points_df.at[event, league_entry_2] = 0
        elif league_entry_1_points < league_entry_2_points:
            points_df.at[event, league_entry_1] = 0
            points_df.at[event, league_entry_2] = 3
        else:
            points_df.at[event, league_entry_1] = 1
            points_df.at[event, league_entry_2] = 1

    points_df_cumsum = points_df.cumsum()
    return points_df_cumsum


# returns dataframe for each players win/loss/draw points each week
def weekly_win_loss_points():
    entry_names = get_entry_names()
    matches = get_matches()
    points_df = weekly_total_points().astype(float)

    for match in matches:
        event = match["event"]
        if match["finished"] == False:
            league_entry_1 = entry_names[match["league_entry_1"]]
            league_entry_2 = entry_names[match["league_entry_2"]]
            points_df.at[event, league_entry_1] = np.nan
            points_df.at[event, league_entry_2] = np.nan
            continue
        league_entry_1 = entry_names[match["league_entry_1"]]
        league_entry_1_points = match["league_entry_1_points"]
        league_entry_2 = entry_names[match["league_entry_2"]]
        league_entry_2_points = match["league_entry_2_points"]

        if league_entry_1_points > league_entry_2_points:
            points_df.at[event, league_entry_1] = 3
            points_df.at[event, league_entry_2] = 0
        elif league_entry_1_points < league_entry_2_points:
            points_df.at[event, league_entry_1] = 0
            points_df.at[event, league_entry_2] = 3
        else:
            points_df.at[event, league_entry_1] = 1
            points_df.at[event, league_entry_2] = 1

    points_df_cumsum = points_df
    return points_df_cumsum

# returns dataframe for each players win/loss/draw points each week
def weekly_win_loss_points_for_table():
    entry_names = get_entry_names()
    matches = get_matches()
    points_df = weekly_total_points().astype(float)

    for match in matches:
        event = match["event"]
        if match["finished"] == True:
            league_entry_1 = entry_names[match["league_entry_1"]]
            league_entry_1_points = match["league_entry_1_points"]
            league_entry_2 = entry_names[match["league_entry_2"]]
            league_entry_2_points = match["league_entry_2_points"]

            if league_entry_1_points > league_entry_2_points:
                points_df.at[event, league_entry_1] = "W"
                points_df.at[event, league_entry_2] = "L"
            elif league_entry_1_points < league_entry_2_points:
                points_df.at[event, league_entry_1] = "L"
                points_df.at[event, league_entry_2] = "W"
            else:
                points_df.at[event, league_entry_1] = "D"
                points_df.at[event, league_entry_2] = "D"

    styled_df = points_df.style.apply(lambda x: x.map(style_results))
    styled_df = styled_df.set_table_styles([{'selector': 'td', 'props': [('text-align', 'center')]}])
    
    return styled_df


# returns dataframe for each players total points their players have scored
def weekly_points_cumulative():
    weekly_total_points_df = weekly_total_points().astype(float)
    df = weekly_total_points_df.cumsum()

    cumulative_avg = df.mean(axis=1)
    new_df_centered = df.subtract(cumulative_avg, axis=0)

    return df


# returns dataframe for each players total win/loss/draw points
def total_win_loss_points():
    points_df = weekly_win_loss_points()
    win_loss_points = points_df.sum().sort_values(ascending=False)

    win_loss_points_df = pd.DataFrame(win_loss_points).reset_index()
    win_loss_points_df.columns = ["Team", "Points"]

    return win_loss_points_df


# returns dataframe for each players total points scored so far in the season
def total_cumulative_points():
    total_points = weekly_total_points().sum().sort_values(ascending=False)

    total_points_df = pd.DataFrame(total_points).reset_index()
    total_points_df.columns = ["Team", "Total Points"]

    return total_points_df


# returns dataframe for each players total transactions
def total_trades():
    total_transactions = weekly_trades().sum().sort_values(ascending=False)

    trades_df = pd.DataFrame(total_transactions).reset_index()
    trades_df.columns = ["Team", "Total Trades"]

    return trades_df


# returns dataframe for each players initial pick position
def pick_order():
    choices = get_choices()

    pick_order_dict = {}

    for choice in choices:
        if choice["round"] == 1:
            pick_order_dict[choice["entry_name"]] = choice["pick"]

    pick_order_df = pd.DataFrame.from_dict(
        pick_order_dict, orient="index", columns=["Pick"]
    )
    pick_order_df = pick_order_df.reset_index()
    pick_order_df = pick_order_df.rename(columns={"index": "Team"})

    return pick_order_df

def make_team_name_link(team_name):
    return f'<form method="POST" action="/manager_search/{team_name}"><button type="submit" class="btn btn-link"><div class="input-group justify-content-center"><span class="input-group-text" id="basic-addon1"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg></span></div></button></form>'


# returns a combined dataframe displaying Team name, pick position, W/L points, Total Points scored, Total Transactions, Point difference
def combined_table():
    # Merge total_points_df with leaderboard_df on 'Team' column
    merged_df = total_cumulative_points().merge(total_win_loss_points(), on="Team")

    # Merge trades_df2 with the above merged dataframe on 'Team' column
    merged_df = merged_df.merge(total_trades(), on="Team")
    merged_df = merged_df.merge(point_differential(), on="Team")

    final_df = merged_df.sort_values("Points", ascending=False)

    # Extract the 'Points' column and store it in a variable
    points = final_df.pop("Points")

    # Insert the 'Points' column before the 'Total Points' column
    final_df.insert(final_df.columns.get_loc("Total Points"), "Points", points)
    final_df.index = np.arange(1, len(final_df) + 1)

    FINALFINAL_DF = pd.merge(pick_order(), final_df, on="Team")
    FINALFINAL_DF[""] = FINALFINAL_DF["Team"].apply(make_team_name_link)
    FINALFINAL_DF = FINALFINAL_DF.sort_values(by="Points", ascending=False)

    # Reset the index, add 1 to start the index at 1, and drop the old index column
    FINALFINAL_DF = FINALFINAL_DF.reset_index(drop=True)
    FINALFINAL_DF.index = FINALFINAL_DF.index + 1

    return FINALFINAL_DF

def premier_league_fixtures():
    upcoming_gameweek = get_upcoming_gameweek()
    fixtures = get_this_weeks_fixtures_response(upcoming_gameweek).json()
    matches = {}
    home_teams = []
    away_teams = []
    index = []
    
    for fixture in fixtures:
        if fixture["event"] == upcoming_gameweek:
            home_team = get_team_name(fixture["team_h"])
            away_team = get_team_name(fixture["team_a"])
            home_teams.append(home_team)
            away_teams.append(away_team)
            index.append("")

    matches["Home"] = home_teams
    matches["Away"] = away_teams

    df = pd.DataFrame(matches, index=index)

    return df

def league_fixtures():
    matches = get_matches()
    gameweek = get_upcoming_gameweek()
    home_teams = []
    home_scores = []
    away_teams = []
    away_scores = []
    index = []
    fixtures = {}

    for match in matches:
        if match["event"] == gameweek:
            home_team = get_manager_team_name_for_fixtures(match["league_entry_1"])
            home_score = match["league_entry_1_points"]
            away_team = get_manager_team_name_for_fixtures(match["league_entry_2"])
            away_score = match["league_entry_2_points"]

            home_teams.append(home_team)
            away_teams.append(away_team)
            home_scores.append(home_score)
            away_scores.append(away_score)

            index.append("")
        
    fixtures["Home"] = home_teams
    fixtures["Home Points"] = home_scores
    fixtures["Away Points"] = away_scores
    fixtures["Away"] = away_teams

    df = pd.DataFrame(fixtures, index=index)

    return df

def get_largest_and_smallest_transactions():
    trades_df = total_trades()

    # Find the entry with the largest total transactions
    largest_entry = trades_df.loc[trades_df['Total Trades'].idxmax()]

    # Find the entry with the smallest total transactions
    smallest_entry = trades_df.loc[trades_df['Total Trades'].idxmin()]

    return largest_entry, smallest_entry

def get_league_name():
    league = get_league()
    league_name = league["name"]

    return league_name

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

def get_previous_gameweek():
    response = get_current_event_response().json()
    week = response["current_event"]

    if response["current_event_finished"] == False:
        previous_gameweek = week - 1
        week = previous_gameweek
    
    return week

def get_highest_score(entry_id):
    matches = get_matches()
    highest_points = 0
    id = get_id_from_entry_id(entry_id)

    for match in matches:
        if match["finished"] == True:
            if match["league_entry_1"] == id and highest_points < match["league_entry_1_points"]:
                highest_points = match["league_entry_1_points"]
            elif match["league_entry_2"] == id and highest_points < match["league_entry_2_points"]:
                highest_points = match["league_entry_2_points"]

    return highest_points

def get_lowest_score(entry_id):
    matches = get_matches()
    lowest_points = 500
    id = get_id_from_entry_id(entry_id)

    for match in matches:
        if match["finished"] == True:
            if match["league_entry_1"] == id and lowest_points > match["league_entry_1_points"]:
                lowest_points = match["league_entry_1_points"]
            elif match["league_entry_2"] == id and lowest_points > match["league_entry_2_points"]:
                lowest_points = match["league_entry_2_points"]

    return lowest_points

def get_average_points(entry_id):
    matches = get_matches()
    gameweek = get_previous_gameweek()
    total_points = 0
    id = get_id_from_entry_id(entry_id)

    for match in matches:
        if match["finished"] == True:
            if match["league_entry_1"] == id:
                total_points += match["league_entry_1_points"]
            elif match["league_entry_2"] == id:
                total_points += match["league_entry_2_points"]
    
    average_points = total_points / gameweek

    rounded_average_points = round(average_points, 1)

    return rounded_average_points

def get_id_from_entry_id(entry_id):
    league_entries = get_league_entries()
    id = 0

    for entry in league_entries:
        if entry["entry_id"] == entry_id:
            id = entry["id"]

    return id

def get_overall_highest_points():
    league_entries = get_league_entries()
    highest_points = 0
    entry_name = ""

    for entry in league_entries:
        points = get_highest_score(entry["entry_id"])
        if points > highest_points:
            highest_points = points
            entry_name = entry["entry_name"]

    return {"highest_points": highest_points, "entry_name": entry_name}

def get_overall_lowest_points():
    league_entries = get_league_entries()
    lowest_points = 500
    entry_name = ""

    for entry in league_entries:
        points = get_lowest_score(entry["entry_id"])
        if points < lowest_points:
            lowest_points = points
            entry_name = entry["entry_name"]

    return {"lowest_points": lowest_points, "entry_name": entry_name}
