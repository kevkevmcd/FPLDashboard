from flask import session

def get_league_code():
    league_code = int(session.get("league_code", 0))
    return league_code