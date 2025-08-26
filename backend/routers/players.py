from fastapi import APIRouter
from models import fetch_one
import sqlite3
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

router = APIRouter(prefix="/api/player", tags=["Players"])


@router.get("/{player_id}")
def get_player(player_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, s.*
        FROM players p
        LEFT JOIN player_career_stats s ON p.playerID = s.playerID
        WHERE p.playerID = ?
    """, (player_id,))
    player = dict(cur.fetchone())
    times_out = player['innings_batted'] - player['not_outs']
    if times_out == 0:
        bat_ave = 0.00
    else:
        bat_ave = player['runs_scored'] / times_out
    player['bat_average'] = bat_ave
    if player['balls_faced'] == 0:
        player['bat_sr'] = 0.00
    else:
        player['bat_sr'] = player['runs_scored'] / player['balls_faced'] * 100
    
    overs_bowled, balls_bowled = player['overs_bowled'].split('.')
    balls_bowled = int(overs_bowled) * 6 + int(balls_bowled)
    if player['wickets_taken'] == 0:
        bowl_ave = 0.00
        bowl_sr = 0.00
    else:
        bowl_ave = player['runs_conceded'] / (player['wickets_taken'])
        bowl_sr = balls_bowled / player['wickets_taken']
    if balls_bowled == 0:
        economy = 0.00
    else:
        economy = player['runs_conceded'] / balls_bowled
    player['bowl_ave'] = bowl_ave
    player['bowl_sr'] = bowl_sr
    player['economy'] = economy
    print(player)
    # Get Team
    cur.execute("SELECT t.teamID, t.name FROM teams t JOIN player_teams pt ON t.teamID = pt.teamID WHERE pt.playerID =?", (player_id,))
    team = cur.fetchone()
    return {"player": player,
            "team": dict(team)
        }
