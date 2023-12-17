from flask import Flask, flash, render_template, request, redirect, url_for
from flask_caching import Cache
from player_query import (
    get_player_info,
    get_player_name,
    get_owner_info,
    get_player_history,
    get_picture
)
from util import(
    get_league_name,
    get_manager_name_without_comma,
    get_league_team_names,
    get_upcoming_gameweek,
    style_results
)
from league_dataframes import(
    combined_table,
    point_differential,
    weekly_trades,
    weekly_win_loss_points_cumsum,
    premier_league_fixtures,
    league_fixtures,
    weekly_win_loss_points_for_table
)
from squad_query import(
    get_manager_id,
    get_squad_info,
    get_team_name
)
from trades import(
    net_points_trades,
    find_trades,
    players_history
)
import os
import pandas as pd

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 600
}

app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

code = 0
# Gets league code from inital page and updates all the global variables to be specific to league
@app.route("/", methods=["GET", "POST"])
def league_code():
    with app.app_context():
        cache.clear()

    if request.method == "POST":
        leagueCode = int(request.form["leagueCode"])
        global code
        code = leagueCode

        if code == 0:
            flash("Please Enter a League Code!")

        return redirect(url_for("home"))

    return render_template("league.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Home page dashboard
# In the render template return you can add any variables to be passed into html (i.e. 'tables', 'titles')
@app.route("/home")
@cache.cached(timeout=1000)
def home():
    league_name = get_league_name()
    gameweek = get_upcoming_gameweek()

    return render_template(
        "home.html",
        tables=[
            combined_table().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
                escape=False,
            ),
            premier_league_fixtures().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
            league_fixtures().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
        ],
        titles=["League Table", "Premier League Fixtures", "League Fixtures"],
        name=f"{league_name}",
        week=f"{gameweek}",
    )


# Weekly table dashboard
@app.route("/weekly_dashboard")
@cache.cached(timeout=1000)
def weekly_dash():
    return render_template(
        "weekly.html",
        tables=[
            weekly_win_loss_points_for_table().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="center",
            ),
            weekly_trades().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            )
        ],
        titles=[
            "Weekly Points Scored",
            "Total Weekly Trades"
        ],
    )

@app.route("/transaction_history")
def transactions_dash():
    return render_template(
        "transactions.html",
        tables=[
            find_trades().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            ),
           net_points_trades().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            )
        ],
        titles=[
            "Trade Tracker",
            "Net Points Trades",
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
    picture = ""
    if request.method == "POST":
        # If get_player_name fails, it will return an empty string (for now).
        player_name = get_player_name(request.form["player_name"])
        if player_name == "":
            player_name = "Player not found"
        else:
            player_info = get_player_info(request.form["player_name"])
            owner_info = get_owner_info(request.form["player_name"])
            picture = get_picture(request.form["player_name"])
            title = "Match History"
            classes = ["table table-dark", "table-striped", "table-hover", "table-sm"]
    return render_template(
        "player_search.html",
        player_name=player_name,
        player_info=player_info,
        owner_info=owner_info,
        picture=picture,
        player_history=get_player_history(player_name).to_html(
            classes=classes,
            justify="left",
            index=False,
        ),
        title=title,
    )

@app.route("/manager_search/<name>", methods=["POST"])
@cache.cached(timeout=1000)
def manager_search(name):
    team_name = ""
    manager_name = ""
    manager_id = 0
    title = ""
    squad = pd.DataFrame()
    classes = []
    team_name = get_team_name(name)
    manager_id = get_manager_id(team_name)

    if team_name == "":
        team_name = "Team not found"
    else:
        manager_name = get_manager_name_without_comma(manager_id)
        squad = get_squad_info(manager_id)     
        title = "Team"
        classes = ["table table-dark", "table-striped", "table-hover", "table-sm"]
    return render_template(
        "manager_search.html",
        team_name=team_name,
        manager_name=manager_name,
        squad=squad.to_html(
            classes=classes,
            justify="left",
            index=False,
        ),
        title=title,
    )
    

if __name__ == "__main__":
    app.run(debug=True)
