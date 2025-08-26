from fastapi import APIRouter
from models import fetch_all, fetch_one
import sqlite3, json
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

router = APIRouter(prefix="", tags=["Live"])


@router.get("/live")
def get_live_match():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    row = cur.execute("SELECT matchID FROM matches WHERE matchPlayed=-1 ORDER BY scheduledDate LIMIT 1").fetchone()
    if row:
        liveID = dict(row)['matchID']
        return liveID
    
    row = cur.execute("SELECT matchID FROM matches WHERE matchPlayed=0 ORDER BY scheduledDate LIMIT 1").fetchone()
    if row:
        liveID = dict(row)['matchID']
        return liveID
    return 