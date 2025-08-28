from fastapi import APIRouter
from models import fetch_all, fetch_one
import sqlite3
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

router = APIRouter(prefix="/api/team", tags=["Teams"])


@router.get("/{team_id}")
def get_team(team_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            teamID AS ID,
            name,
            color,
            gamesPlayed AS played,
            gamesWon AS won,
            gamesLost AS lost,
            gamesTied as tied,
            CASE
                WHEN oversFaced > 0 AND oversBowled > 0
                THEN ROUND((runsScored * 1.0 / oversFaced) - (runsConceded * 1.0 / oversBowled), 2)
                ELSE 0
            END AS NRR    
        FROM teams WHERE teamID = ?
    """, (team_id,))
    team = cur.fetchone()
    if not team:
        conn.close()
        return {"error": "team not found"}
    
    # Get players
    cur.execute("SELECT p.* FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (team_id,))
    players = [dict(row) for row in cur.fetchall()]

    

    conn.close()

    return {
        "team": dict(team),
        "players": players,
    }


@router.get("/")
def league_table():
    query = """
    SELECT * FROM teams
    ORDER BY gamesWon DESC, (runsScored*1.0/oversFaced - runsConceded*1.0/oversBowled) DESC
    """
    return fetch_all(query)
