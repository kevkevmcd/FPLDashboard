from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from collections import defaultdict
from pprint import pprint

app = Flask(__name__)

code = 0

response = requests.get(f"https://draft.premierleague.com/api/league/{code}/details")
transaction_response = requests.get(f"https://draft.premierleague.com/api/draft/league/{code}/transactions")
choices_response = requests.get(f"https://draft.premierleague.com/api/draft/{code}/choices")
data = response.json()

matches = data["matches"]
league_entries = data["league_entries"]

columns = []
for items in league_entries:
    columns.append(items["id"])
row = [x + 1 for x in range(38)]

entry_names = {}
for items in league_entries:
    entry_id = items["id"]
    entry_name = items["entry_name"]
    entry_names[entry_id] = entry_name

@app.route("/", methods=["GET", "POST"])
def league_code():
    if request.method == "POST":
        leagueCode = request.form["leagueCode"]

        global code
        code = leagueCode

        global response
        response = requests.get(f"https://draft.premierleague.com/api/league/{code}/details")

        global transaction_response
        transaction_response = requests.get(f"https://draft.premierleague.com/api/draft/league/{code}/transactions")

        global choices_response
        choices_response = requests.get(f"https://draft.premierleague.com/api/draft/{code}/choices")

        global data
        data = response.json()

        return redirect(url_for('home'))
    
    return render_template("league.html")

@app.route("/home")
def home():
    return render_template('home.html',  tables=[point_differential().to_html(classes='data'), weekly_trades().to_html(classes='data')], titles=["Point Differentials", "Transactions"])

def point_differential():
    league_entries = data['league_entries']
    entry_names = {entry['id']: entry['entry_name'] for entry in league_entries}
    standings = data['standings']

    team_diffs = {}
    for team in standings:
        team_name = entry_names[team['league_entry']]
        points_for = team['points_for']
        points_against = team['points_against']
        diff = points_for - points_against
        team_diffs[team_name] = diff

    df = pd.DataFrame.from_dict(team_diffs, orient='index', columns=['Point Difference'])
    df = df.sort_values(by='Point Difference', ascending=False)
    df = df.reset_index()
    df = df.rename(columns={"index": "Team", "Point Difference": "Point Difference"})

    return df

def weekly_trades():
    transactions = transaction_response.json()["transactions"]

    teams = {entry["entry_id"]: entry["entry_name"] for entry in data["league_entries"]}
    columns = list(teams.values())
    index = [x + 1 for x in range(38)]
    df = pd.DataFrame(0, columns=columns, index=index)

    for transaction in transactions:
        event = transaction["event"]
        team_id = transaction["entry"]
        team_name = teams.get(team_id)
        result = transaction["result"]

        if team_name and result == "a":
            df.at[event, team_name] += 1

    return df

def weekly_total_points():
    new_columns = [entry_names[x] for x in columns]
    df = pd.DataFrame(data, columns=new_columns, index=row)

    for match in matches:
        event = match["event"]
        league_entry_1 = match["league_entry_1"]
        league_entry_1_points = match["league_entry_1_points"]
        league_entry_2 = match["league_entry_2"]
        league_entry_2_points = match["league_entry_2_points"]

        df.at[event, entry_names[league_entry_1]] = league_entry_1_points
        df.at[event, entry_names[league_entry_2]] = league_entry_2_points

    return df

def weekly_win_loss_points():
    points_df = weekly_total_points().copy().astype(float)

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

def weekly_points_cumulative():
    weekly_total_points_df = weekly_total_points().astype(float)
    df = weekly_total_points_df.cumsum()

    cumulative_avg = df.mean(axis=1)
    new_df_centered = df.subtract(cumulative_avg, axis=0)

    return df

def total_win_loss_points():
    points_df = weekly_total_points().copy().astype(float)
    win_loss_points = points_df.sum().sort_values(ascending=False)

    win_loss_points_df = pd.DataFrame(win_loss_points).reset_index()
    win_loss_points_df.columns = ['Team', 'Points']

    return win_loss_points_df

def total_cumulative_points():
    total_points = weekly_total_points().sum().sort_values(ascending=False)

    total_points_df = pd.DataFrame(total_points).reset_index()
    total_points_df.columns = ['Team', 'Total Points']

    return total_points_df

def total_trades():
    total_transactions = weekly_trades().sum().sort_values(ascending=False)

    trades_df = pd.DataFrame(total_transactions).reset_index()
    trades_df.columns = ['Team', 'Total Trades']

    return trades_df

def pick_order():
    fixture_list = choices_response

    pick_order_dict = {}

    for choice in fixture_list.json()['choices']:
        if choice['round'] == 1:
            pick_order_dict[choice['entry_name']] = choice['pick']

    pick_order_df = pd.DataFrame.from_dict(pick_order_dict, orient='index', columns=['Pick'])
    pick_order_df = pick_order_df.reset_index()
    pick_order_df = pick_order_df.rename(columns={'index': 'Team'})

    return pick_order_df

def combined_table():
    # Merge total_points_df with leaderboard_df on 'Team' column
    merged_df = total_cumulative_points().merge(total_win_loss_points(), on='Team')

    # Merge trades_df2 with the above merged dataframe on 'Team' column
    merged_df = merged_df.merge(total_trades(), on='Team')
    merged_df = merged_df.merge(point_differential(), on='Team')

    final_df = merged_df.sort_values('Points', ascending=False)

    points_df_cumsum = weekly_win_loss_points().copy()

    last_valid_index = points_df_cumsum.apply(pd.Series.last_valid_index)
    last_valid_column = points_df_cumsum.idxmax()
    current_gw = last_valid_index[last_valid_column] 
    final_df['Avg Gameweek Points'] = final_df['Total Points'] / current_gw
    final_df['Avg Gameweek Points'] = final_df['Avg Gameweek Points'].round(1)

    # Extract the 'Points' column and store it in a variable
    points = final_df.pop('Points')

    # Insert the 'Points' column before the 'Total Points' column
    final_df.insert(final_df.columns.get_loc('Total Points'), 'Points', points)
    final_df = final_df.set_index(pd.Index(np.arange(1, len(final_df)+1)))

    FINALFINAL_DF = pd.merge(pick_order(), final_df, on='Team')
    FINALFINAL_DF = FINALFINAL_DF.sort_values(by='Points', ascending=False)
    FINALFINAL_DF = FINALFINAL_DF.reset_index().drop('index', axis=1)

    return FINALFINAL_DF

if __name__ == '__main__':
    app.run(debug=True)