from flask import Flask, flash, render_template, request, redirect, url_for
from player_query import (
    get_player_info,
    get_player_name,
    get_owner_info,
    get_player_history,
)
from util import(
    get_league_name
)
from league_dataframes import(
    combined_table,
    point_differential,
    weekly_total_points,
    weekly_trades,
    weekly_win_loss_points_cumsum
)
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

code = 0
# Gets league code from inital page and updates all the global variables to be specific to league
@app.route("/", methods=["GET", "POST"])
def league_code():
    if request.method == "POST":
        leagueCode = int(request.form["leagueCode"])
        global code
        code = leagueCode
        print(f"{code}")

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
def home():
    league_name = get_league_name()

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

if __name__ == "__main__":
    app.run(debug=True)
