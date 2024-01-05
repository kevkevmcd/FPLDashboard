from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_caching import Cache
import os
import pandas as pd
from player_query import (
    get_player_info,
    get_player_name,
    get_owner_info,
    get_player_history,
    get_picture
)
from league_dataframes import(
    combined_table,
    weekly_trades,
    premier_league_fixtures,
    league_fixtures,
    weekly_win_loss_points_for_table,
    get_largest_and_smallest_transactions,
    get_league_name,
    get_upcoming_gameweek,
    get_average_points,
    get_highest_score,
    get_lowest_score,
    get_overall_highest_points,
    get_overall_lowest_points
)
from squad_query import(
    get_manager_id,
    get_squad_info,
    get_team_name,
    get_manager_name_without_comma
)

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

# Gets league code from inital page and updates all the global variables to be specific to league
@app.route("/", methods=["GET", "POST"])
def league_code():
    with app.app_context():
        cache.clear()

    if request.method == "POST":
        league_code = int(request.form["leagueCode"])

        if league_code == 0:
            flash("Please Enter a League Code!")
        else:
            session["league_code"] = league_code

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
    highest_result = get_overall_highest_points()
    lowest_result = get_overall_lowest_points()
    largest_entry, smallest_entry = get_largest_and_smallest_transactions()
    return render_template(
        "weekly.html",
        tables=[
            weekly_win_loss_points_for_table().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="center"
            ),
            weekly_trades().to_html(
                classes=["table table-dark", "table-striped", "table-hover"],
                justify="left",
            )
        ],
        titles=[
            "Weekly Win/Loss",
            "Weekly Total Trades"
        ],
        highest_points_team=highest_result["entry_name"],
        highest_points=highest_result["highest_points"],
        lowest_points_team=lowest_result["entry_name"],
        lowest_points=lowest_result["lowest_points"],
        largest_entry_team=largest_entry["Team"],
        largest_entry_trades=largest_entry["Total Trades"],
        smallest_entry_team=smallest_entry["Team"],
        smallest_entry_trades=smallest_entry["Total Trades"]
    )

# Player search form.
@app.route('/player_search/', methods=['GET'])
def player_search_form():
    return render_template("player_search_form.html")

# Player search dashboard.
@app.route("/player_search/", methods=["POST"])
def player_search():
    input_player_name = get_player_name(request.form["player_name"])

    if input_player_name:
        # Redirect to the search results page with the player_name in the URL
        return redirect(url_for("search_results", player_name=input_player_name))

    # If player_name is not provided, render the initial search form template
    return render_template("player_search_form.html")

# Search results page.
@app.route("/search_results/<string:player_name>", methods=["GET"])
@cache.cached(timeout=1000)
def search_results(player_name):
    player_info = get_player_info(player_name)
    owner_info = get_owner_info(player_name)
    picture = get_picture(player_name)
    title = "Match History"
    classes = ["table", "table-dark", "table-striped", "table-hover", "table-sm"]

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
        highest_score = get_highest_score(manager_id)
        lowest_score = get_lowest_score(manager_id)
        average_points = get_average_points(manager_id)
        title = "Team"
        classes = ["table table-dark", "table-striped", "table-hover", "table-sm"]
    return render_template(
        "manager_search.html",
        team_name=team_name,
        manager_name=manager_name,
        highest_score=highest_score,
        lowest_score=lowest_score,
        average_points=average_points,
        squad=squad.to_html(
            classes=classes,
            justify="left",
            index=False,
        ),
        title=title,
    )
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(3000), debug=True)
