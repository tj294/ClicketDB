from fastapi import APIRouter
from models import fetch_all, fetch_one
import sqlite3, json
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

router = APIRouter(prefix="/api/season", tags=["Season"])


@router.get("/{seasonID}")
def upcoming_matches(seasonID: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
    SELECT m.matchID, m.season, m.matchNo, m.round, m.homeTeamID, ht.name AS homeTeamName, ht.color AS homeTeamColor, m.awayTeamID, at.name AS awayTeamName, at.color AS awayTeamColor, m.scheduledDate, m.matchPlayed, m.result FROM matches m JOIN teams ht ON m.homeTeamID = ht.teamID JOIN teams at ON m.awayTeamID = at.teamID WHERE season = ? ORDER BY round ASC, matchNo ASC;
    """, (seasonID,))
    matches = cur.fetchall()
    out_matches = []
    for match in matches:
        info = dict(match)
        if info['homeTeamName'] in info['result']:
            info['winColor'] = info['homeTeamColor']
        elif info['awayTeamName'] in info['result']:
            info['winColor'] = info['awayTeamColor']
        else:
            info['winColor'] = '#FFFFFF'
        out_matches.append(info)
    return out_matches

