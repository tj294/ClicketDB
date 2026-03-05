from fastapi import APIRouter
from models import fetch_all, fetch_one

router = APIRouter(prefix="/api/matches", tags=["Matches"])


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

@router.get("/recent/{homeTeamID}/{awayTeamID}")
def get_recent_results(homeTeamID, awayTeamID):
    query = f"""SELECT
                    matchID, homeTeamID, awayTeamID, winTeamID 
                FROM 
                    matches 
                WHERE 
                    matchPlayed = 1 
                AND 
                    (homeTeamID={homeTeamID} OR awayTeamID={homeTeamID}) 
                AND 
                    (homeTeamID={awayTeamID} OR awayTeamID={awayTeamID}) 
                ORDER BY matchNo DESC 
                LIMIT 5
            """
    return fetch_all(query)