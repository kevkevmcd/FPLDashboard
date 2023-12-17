import pandas as pd
import util
import numpy as np

# returns dataframe for player point differentials
def point_differential():
    entry_names = util.get_entry_names()
    standings = util.get_standings()

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
    transactions = util.get_transactions()
    league_entries = util.get_league_entries()

    teams = {entry["entry_id"]: entry["entry_name"] for entry in league_entries}
    columns = list(teams.values())
    gameweek = util.get_upcoming_gameweek()
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
    response = util.get_details_response().json()
    entry_names = util.get_entry_names()
    columns = util.get_columns()
    gameweek = util.get_upcoming_gameweek()
    row = [x + 1 for x in range(gameweek)]
    matches = util.get_matches()

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
    entry_names = util.get_entry_names()
    matches = util.get_matches()
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
    entry_names = util.get_entry_names()
    matches = util.get_matches()
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
    entry_names = util.get_entry_names()
    matches = util.get_matches()
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

    points_df_cumsum = points_df.style.applymap(util.style_results)
    styled_df = points_df_cumsum.set_table_styles([{'selector': 'td', 'props': [('text-align', 'center')]}])
    
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
    choices = util.get_choices()

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
    FINALFINAL_DF[""] = FINALFINAL_DF["Team"].apply(util.make_team_name_link)
    FINALFINAL_DF = FINALFINAL_DF.sort_values(by="Points", ascending=False)

    # Reset the index, add 1 to start the index at 1, and drop the old index column
    FINALFINAL_DF = FINALFINAL_DF.reset_index(drop=True)
    FINALFINAL_DF.index = FINALFINAL_DF.index + 1

    return FINALFINAL_DF

def premier_league_fixtures():
    upcoming_gameweek = util.get_upcoming_gameweek()
    fixtures = util.get_this_weeks_fixtures_response(upcoming_gameweek).json()
    matches = {}
    home_teams = []
    away_teams = []
    index = []
    
    for fixture in fixtures:
        if fixture["event"] == upcoming_gameweek:
            home_team = util.get_team_name(fixture["team_h"])
            away_team = util.get_team_name(fixture["team_a"])
            home_teams.append(home_team)
            away_teams.append(away_team)
            index.append("")

    matches["Home"] = home_teams
    matches["Away"] = away_teams

    df = pd.DataFrame(matches, index=index)

    return df

def league_fixtures():
    matches = util.get_matches()
    gameweek = util.get_upcoming_gameweek()
    home_teams = []
    home_scores = []
    away_teams = []
    away_scores = []
    index = []
    fixtures = {}

    for match in matches:
        if match["event"] == gameweek:
            home_team = util.get_manager_team_name_for_fixtures(match["league_entry_1"])
            home_score = match["league_entry_1_points"]
            away_team = util.get_manager_team_name_for_fixtures(match["league_entry_2"])
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
