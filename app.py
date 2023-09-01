from flask import Flask, render_template
import pandas as pd
import requests
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from collections import defaultdict
from pprint import pprint

app = Flask(__name__)

response = requests.get("https://draft.premierleague.com/api/league/507/details")
data = response.json()

@app.route("/")
def home():
    return render_template('home.html',  tables=[point_differential().to_html(classes='data'), trades().to_html(classes='data')], titles=["Point Differentials", "Transactions"])

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

    difference_points_df = pd.DataFrame.from_dict(team_diffs, orient='index', columns=['Point Difference'])
    difference_points_df = difference_points_df.sort_values(by='Point Difference', ascending=False)
    difference_points_df = difference_points_df.reset_index()
    difference_points_df = difference_points_df.rename(columns={"index": "Team", "Point Difference": "Point Difference"})

    return difference_points_df

def trades():
    response2 = requests.get("https://draft.premierleague.com/api/draft/league/507/transactions")
    transactions = response2.json()["transactions"]

    teams = {entry["entry_id"]: entry["entry_name"] for entry in data["league_entries"]}
    columns = list(teams.values())
    index = [x + 1 for x in range(38)]
    trades_df = pd.DataFrame(0, columns=columns, index=index)

    for transaction in transactions:
        event = transaction["event"]
        team_id = transaction["entry"]
        team_name = teams.get(team_id)
        result = transaction["result"]

        if team_name and result == "a":
            trades_df.at[event, team_name] += 1

    return trades_df

if __name__ == '__main__':
    app.run(debug=True)