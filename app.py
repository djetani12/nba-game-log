from flask import Flask, request, jsonify, render_template
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

app = Flask(__name__)

def get_player_id(player_name):
    all_players = players.get_players()
    for p in all_players:
        if p['full_name'].lower() == player_name.lower():
            return p['id']
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search_player():
    name = request.args.get("name")
    season = request.args.get("season")

    player_id = get_player_id(name)
    if not player_id:
        return jsonify({"error": "Player not found"})

    gamelog = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=season
    )

    df = gamelog.get_data_frames()[0]

    df = df[[
        "GAME_DATE", "MATCHUP", "MIN", "PTS", "REB", "AST",
        "STL", "BLK", "FGM", "FGA", "FG_PCT",
        "FG3M", "FG3A", "FG3_PCT",
        "FTM", "FTA", "FT_PCT",
        "OREB", "DREB", "TOV", "PF"
    ]]

    # Fix opponent display
    def format_matchup(m):
        parts = m.split(" ")
        if "@" in parts:
            return "@" + parts[-1]
        else:
            return "vs " + parts[-1]

    df["MATCHUP"] = df["MATCHUP"].apply(format_matchup)

    df.columns = [
        "Date", "Opponent", "MIN", "PTS", "REB", "AST",
        "STL", "BLK", "FGM", "FGA", "FG%",
        "3PM", "3PA", "3P%",
        "FTM", "FTA", "FT%",
        "OREB", "DREB", "TOV", "PF"
    ]

    return df.to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=True)