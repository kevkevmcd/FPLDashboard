from flask import Flask, render_template, request, redirect, url_for
from player_query import (
    get_player_info,
    get_player_name,
    get_owner_info,
    get_player_history,
)
import pandas as pd
import requests
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import os

app = Flask(__name__)

# Global Variables
code = 0

response = requests.get(f"https://draft.premierleague.com/api/league/{code}/details")
transaction_response = requests.get(
    f"https://draft.premierleague.com/api/draft/league/{code}/transactions"
)
choices_response = requests.get(
    f"https://draft.premierleague.com/api/draft/{code}/choices"
)
static_elements = requests.get(
    "https://fantasy.premierleague.com/api/bootstrap-static/"
)
element_status = requests.get(
    f"https://draft.premierleague.com/api/league/{code}/element-status"
)
league_details = requests.get(
    f"https://draft.premierleague.com/api/league/{code}/details"
)
data = response.json()

matches = ""
league_entries = ""
row = []
columns = []
entry_names = {}
league = {}
league_name = ""

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


# Gets league code from inital page and updates all the global variables to be specific to league
@app.route("/", methods=["GET", "POST"])
def league_code():
    if request.method == "POST":
        leagueCode = request.form["leagueCode"]

        global code
        code = leagueCode

        global response
        response = requests.get(
            f"https://draft.premierleague.com/api/league/{code}/details"
        )

        global transaction_response
        transaction_response = requests.get(
            f"https://draft.premierleague.com/api/draft/league/{code}/transactions"
        )

        global choices_response
        choices_response = requests.get(
            f"https://draft.premierleague.com/api/draft/{code}/choices"
        )

        global static_elements
        static_elements = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/"
        )

        global element_status
        element_status = requests.get(
            f"https://draft.premierleague.com/api/league/{code}/element-status"
        )

        global league_details
        league_details = requests.get(
            f"https://draft.premierleague.com/api/league/{code}/details"
        )

        global data
        data = response.json()

        global matches
        matches = data["matches"]

        global league_entries
        league_entries = data["league_entries"]

        global columns
        for items in league_entries:
            columns.append(items["id"])

        global row
        row = [x + 1 for x in range(38)]

        global entry_names
        for items in league_entries:
            entry_id = items["id"]
            entry_name = items["entry_name"]
            entry_names[entry_id] = entry_name

        global league
        league = data["league"]

        global league_name
        league_name = league["name"]

        return redirect(url_for("home"))

    return render_template("league.html")


# Home page dashboard
# In the render template return you can add any variables to be passed into html (i.e. 'tables', 'titles')
@app.route("/home")
def home():
    return render_template(
        "home.html",
        tables=[
            combined_table().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            )
        ],
        titles=["League Table"],
        name=f"{league_name}",
    )


# Weekly table dashboard
@app.route("/weekly_dashboard")
def weekly_dash():
    return render_template(
        "weekly.html",
        tables=[
            weekly_total_points().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
            weekly_win_loss_points_cumsum().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
            weekly_trades().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
            point_differential().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
        ],
        titles=[
            "Weekly Points Scored",
            "Points Per Week",
            "Total Weekly Trades",
            "Point Differentials",
        ],
    )


# Player search dashboard.
@app.route("/player_search", methods=["GET", "POST"])
def player_search():
    # Initialize variables so that GET method has default values to pass to player_search.html
    player_name = ""
    player_info = ""
    owner_info = ""
    title = ""
    classes = []
    if request.method == "POST":
        # If get_player_name fails, it will return an empty string (for now).
        player_name = get_player_name(request.form["player_name"])
        if player_name == "":
            player_name = "Player not found"
        else:
            player_info = get_player_info(request.form["player_name"])
            owner_info = get_owner_info(request.form["player_name"])
            title = "Match History"
            classes = ["table table-dark", "table-striped", "table-hover"]
    return render_template(
        "player_search.html",
        player_name=player_name,
        player_info=player_info,
        owner_info=owner_info,
        player_history=get_player_history(player_name).to_html(
            classes=classes,
            justify="left",
            index=False,
        ),
        title=title,
    )


# returns dataframe for player point differentials
def point_differential():
    league_entries = data["league_entries"]
    entry_names = {entry["id"]: entry["entry_name"] for entry in league_entries}
    standings = data["standings"]

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


# returns dataframe for each players total amount of points scored per week
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


# returns dataframe for each players win/loss/draw points each week added to what they already had
def weekly_win_loss_points_cumsum():
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
    fixture_list = choices_response

    pick_order_dict = {}

    for choice in fixture_list.json()["choices"]:
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

    # points_df_cumsum = weekly_win_loss_points()

    # last_valid_index = points_df_cumsum.notna()[::-1].idxmax()
    # last_valid_column = last_valid_index.idxmax()
    # current_gw = last_valid_index[last_valid_column]
    # final_df['Avg Gameweek Points'] = final_df['Total Points'] / current_gw
    # final_df['Avg Gameweek Points'] = final_df['Avg Gameweek Points'].round(1)

    # Extract the 'Points' column and store it in a variable
    points = final_df.pop("Points")

    # Insert the 'Points' column before the 'Total Points' column
    final_df.insert(final_df.columns.get_loc("Total Points"), "Points", points)
    final_df = final_df.set_index(pd.Index(np.arange(1, len(final_df) + 1)))

    FINALFINAL_DF = pd.merge(pick_order(), final_df, on="Team")
    FINALFINAL_DF = FINALFINAL_DF.sort_values(by="Points", ascending=False)
    FINALFINAL_DF = FINALFINAL_DF.reset_index().drop("index", axis=1)

    return FINALFINAL_DF


if __name__ == "__main__":
    app.run(debug=True)
