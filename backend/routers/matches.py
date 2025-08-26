from fastapi import APIRouter
from models import fetch_all, fetch_one

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/upcoming")
def upcoming_matches():
    query = "SELECT * FROM matches WHERE matchPlayed = 0 AND scheduledDate >= date('now', 'localtime') ORDER BY scheduledDate ASC LIMIT 12"
    return fetch_all(query)


@router.get("/live")
def live_match():
    query = "SELECT * FROM matches WHERE matchPlayed = 0 AND match_time <= datetime('now') ORDER BY match_time LIMIT 1"
    return fetch_one(query)


@router.get("/past")
def past_matches():
    query = "SELECT * FROM matches WHERE matchPlayed = 1 ORDER BY scheduledDate DESC"
    return fetch_all(query)
