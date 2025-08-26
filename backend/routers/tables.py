from fastapi import APIRouter
from models import fetch_all, fetch_one
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

router = APIRouter(prefix="/api/tables", tags=["Tables"])


@router.get("/{season_id}")
def previous_league_table():
    query = """
    SELECT * FROM teams
    ORDER BY gamesWon DESC, (runsScored*1.0/oversFaced - runsConceded*1.0/oversBowled) DESC
    """
    return fetch_all(query)


@router.get("/")
def league_table():
    query = """
    SELECT * FROM teams
    ORDER BY gamesWon DESC, (runsScored*1.0/oversFaced - runsConceded*1.0/oversBowled) DESC
    """
    return fetch_all(query)
