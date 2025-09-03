from fastapi import FastAPI, WebSocket, BackgroundTasks
from models import fetch_all
from routers import matches, teams, players, live, games, season, account
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, final
from datetime import datetime, timedelta
import sqlite3, json, asyncio
from match_sim import simulate_match
from generation import regenerate_fixtures
from classes import ConnectionManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
from os import getenv
import logging
from fastapi.logger import logger
from filelock import FileLock, Timeout

load_dotenv()
DB_NAME = getenv("DBNAME")

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)

app = FastAPI()
manager = ConnectionManager()
scheduler = AsyncIOScheduler(
        jobstores={'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
        )

#origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"]
origins = ["https://clicket-game.com", "http://clicket-game.com", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow React frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(live.router)
app.include_router(games.router)
app.include_router(season.router)
app.include_router(account.router)

async def check_matches():
    lock = FileLock("match_scheduler.lock")
    
    try:
        lock.acquire(timeout=1)
        logger.info("Lock acquired, checking for matches")

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        now = datetime.now().astimezone()
        logger.info(f"Time is: {now}")

        cur.execute("SELECT matchID FROM matches WHERE scheduledDate <= ? AND matchPlayed = 0", (now,))
        matches = cur.fetchall()
        logger.info(f"Found matches: {matches}")

        for (matchID,) in matches:
            logger.info(f"Starting match {matchID}")
            asyncio.create_task(simulate_match(matchID, manager))
    except Timeout:
        logger.info("Another scheduler is running, skip!")

    finally:
        if lock.is_locked:
            lock.release()
            logger.info("Lock Released.")

async def generate_season():
    lock = FileLock("season_gen.lock")

    try:
        lock.acquire(timeout=1)
        logger.info("Lock acquired, generating season")
        today = datetime.today()
        day_diff = (0 - today.weekday()) % 7
        base_date = today.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=day_diff)
        regenerate_fixtures(base_date)
    except Timeout:
        logger.info("Another scheduler is running, skip!")
    
    finally:
         if lock.is_locked:
              lock.release()
              logger.info("Lock Released.")



@app.on_event("startup")
def start_scheduler():
    now = datetime.now()
    start_date = "2025-08-24 09:00:00"
    season_gen_date = "2025-08-31 17:30:00"
    logger.info(f"{now}: Starting Scheduler, every hour from {start_date}")
    scheduler.add_job(check_matches, "interval", hours=1, start_date=start_date)
    scheduler.add_job(generate_season, "interval", days=7, start_date=season_gen_date)
    scheduler.start()

@app.post("/start_match/{matchID}")
async def start_match(matchID: int, background_tasks: BackgroundTasks):
    """
    Call this to start match MatchID
    """
    print("main: ", manager, manager.active_connections)
    background_tasks.add_task(simulate_match, matchID, manager)

@app.get("/api/upcoming_matches")
def get_upcoming_matches():
    conn = sqlite3.connect("cricket_sim.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT m.matchID AS ID, m.scheduledDate, t1.name AS team1, t2.name AS team2
        FROM matches m
        JOIN teams t1 ON m.homeTeamID = t1.teamID
        JOIN teams t2 ON m.awayTeamID = t2.teamID
        WHERE m.matchPlayed = 0
        ORDER BY m.scheduledDate ASC
        LIMIT 12
    """)

    matches = []
    for row in cur.fetchall():
        matches.append({
            "ID": row["ID"],
            "team1": row["team1"],
            "team2": row["team2"],
            "scheduledDate": row["scheduledDate"]
        })

    conn.close()
    return matches

@app.get("/api/league_table")
def get_league_table():
    conn = sqlite3.connect("cricket_sim.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            teamID AS ID,
            name,
            gamesPlayed AS played,
            gamesWon AS won,
            gamesLost AS lost,
            gamesTied AS tied,
            CASE 
                WHEN oversFaced > 0 AND oversBowled > 0
                THEN ROUND((runsScored * 1.0 / oversFaced) - (runsConceded * 1.0 / oversBowled), 2)
                ELSE 0
            END AS NRR
        FROM teams
        ORDER BY (gamesWon*2.0 + gamesTied) DESC, NRR DESC
    """)
    league = []
    for row in cur.fetchall():
        nrr = f"{row['NRR']:+.2f}"
        league.append({
            "ID": row['ID'],
            "name": row["name"],
            "played": row['played'],
            "won": row['won'],
            "lost": row['lost'],
            "tied": row['tied'],
            "NRR": nrr,
        })
    
    conn.close()
    return league

@app.websocket("/ws/game/{matchID}")
async def websocket_endpoint(websocket: WebSocket, matchID: int):
    await manager.connect(matchID, websocket)
    print(manager.active_connections)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute(f"SELECT * FROM matches WHERE matchID = ?;", (matchID,)).fetchone()
    # conn.close()
    info = dict(row)
    if info['matchPlayed'] == 0:
        homeTeamInfo = cur.execute("SELECT * FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()
        homeTeamName = homeTeamInfo['name']
        homeTeamColor = homeTeamInfo['color']
        homeTeamPoints = homeTeamInfo['gamesWon']*2 + 1*homeTeamInfo['gamesTied']
        try:
            hTNRR = (homeTeamInfo['runsScored'] / homeTeamInfo['oversFaced']) - (homeTeamInfo['runsConceded']/homeTeamInfo['oversBowled'])
        except:
            hTNRR = 0
        homeTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['homeTeamID'], ))
        awayTeamInfo = cur.execute("SELECT * FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()
        awayTeamName = awayTeamInfo['name']
        awayTeamColor = awayTeamInfo['color']
        awayTeamPoints = awayTeamInfo['gamesWon']*2 + 1*awayTeamInfo['gamesTied']
        try:
            aTNRR = (awayTeamInfo['runsScored'] / awayTeamInfo['oversFaced']) - (awayTeamInfo['runsConceded']/awayTeamInfo['oversBowled'])
        except:
            aTNRR = 0
        awayTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['awayTeamID'], ))
        liveInfo = {
            "status": "Upcoming",
            "season": info['season'],
            "match": info['matchNo'],
            "homeTeam": homeTeamName,
            "homeTeamID": info['homeTeamID'],
            "homeTeamColor": homeTeamColor,
            "homeTeamTable": {
                "M": homeTeamInfo['gamesPlayed'],
                "W": homeTeamInfo['gamesWon'],
                "L": homeTeamInfo['gamesLost'],
                "PTS": homeTeamPoints,
                "NRR": hTNRR
            },
            "homePlayers": homeTeamPlayers,
            "awayTeam": awayTeamName,
            "awayTeamID": info['awayTeamID'],
            "awayTeamColor": awayTeamColor,
            "awayTeamTable": {
                "M": awayTeamInfo['gamesPlayed'],
                "W": awayTeamInfo['gamesWon'],
                "L": awayTeamInfo['gamesLost'],
                "PTS": awayTeamPoints,
                "NRR": aTNRR
            },
            "awayPlayers": awayTeamPlayers,
            "date": info['scheduledDate']
        }
        conn.close()
        await websocket.send_text(json.dumps(liveInfo))
    elif info['matchPlayed'] == 1:
        # Needs refining to only necessary information
        homeTeamInfo = cur.execute("SELECT name, color FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()
        homeTeamName = homeTeamInfo['name']
        homeTeamColor = homeTeamInfo['color']
        print(homeTeamColor)
        awayTeamInfo = cur.execute("SELECT name, color FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()
        awayTeamName = awayTeamInfo['name']
        awayTeamColor = awayTeamInfo['color']
        if info['batFirstID'] == info['homeTeamID']:
            batFirstName = homeTeamName
            batSecondID = info['awayTeamID']
            batSecondName = awayTeamName
        else:
            batFirstName = awayTeamName
            batSecondID = info['homeTeamID']
            batSecondName = homeTeamName
        if info['bFOvers'] == '19.6':
            info['bFOvers'] = '20.0'
        # Calculate Run Rate
        if type(info['bFOvers']) == float:
                balls_faced = 0
        else:
                balls_faced = int(info['bFOvers'].split('.')[0]) * 6 + int(info['bFOvers'].split('.')[1])
        runs_scored = info['bFRuns']
        if balls_faced == 0:
                bfCRR = 0.00
        else:
                bfCRR = runs_scored / (int(balls_faced) / 6)
        if info['bSOvers'] == "YTB":
            bsCRR = 0.00
            bsRRR = 0.00
        else:
            balls_faced = int(info['bSOvers'].split('.')[0]) * 6 + int(info['bSOvers'].split('.')[1])
            balls_remaining = 120-balls_faced
            bsCRR = info['bSRuns'] / (balls_faced/6)
            if balls_remaining > 0:
                bsRRR = (info['bFRuns'] - info['bSRuns']) / (balls_remaining/6)
            else:
                bsRRR = 0
        if info['sbattingCard'] == None:
            sbattingCard = None
            syetToBat = None
            sbowlingCard = None
        else:
            sbattingCard = json.loads(info['sbattingCard'])
            syetToBat = json.loads(info['syetToBat'])
            sbowlingCard = json.loads(info['sbowlingCard'])
        # logText = json.loads(info['log'])
        logText = []
        for log in json.loads(info['log']):
                logText.append(json.loads(log))
        liveInfo = {
            "status": "played",
            "season": info['season'],
            "match": info['matchNo'],
            "homeTeam": homeTeamName,
            "homeTeamID": info['homeTeamID'],
            "homeTeamColor": homeTeamColor,
            "awayTeam": awayTeamName,
            "awayTeamID": info['awayTeamID'],
            "awayTeamColor": awayTeamColor,
            "bfName": batFirstName,
            "bfID": info['batFirstID'],
            "bsName": batSecondName,
            "bsID": batSecondID,
            "bfRuns": info['bFRuns'],
            "bfWickets": info['bFWickets'],
            "bfOvers": info['bFOvers'],
            "bfCRR": bfCRR,
            "bsRuns": info['bSRuns'],
            "bsWickets": info['bSWickets'],
            "bsOvers": info['bSOvers'],
            "bsCRR": bsCRR,
            "bsRRR": bsRRR,
            "overResults": info['overResults'],
            "ballEvent": info['ballEvent'],
            "ballText": info['ballText'],
            "currentOver": info['currentOver'],
            "currentBall": info['currentBall'],
            "strikeID": info['batter1ID'],
            "strikeFName": info['batter1FName'],
            "strikeLName": info['batter1LName'],
            "strikeRuns": info['batter1Runs'],
            "strikeBalls": info['batter1Balls'],
            "strikeFours": info['batter1Fours'],
            "strikeSixes": info['batter1Sixes'],
            "strikeSR": info['batter1SR'],
            "nstrikeID": info['batter2ID'],
            "nstrikeFName": info['batter2FName'],
            "nstrikeLName": info['batter2LName'],
            "nstrikeRuns": info['batter2Runs'],
            "nstrikeBalls": info['batter2Balls'],
            "nstrikeFours": info['batter2Fours'],
            "nstrikeSixes": info['batter2Sixes'],
            "nstrikeSR": info['batter2SR'],
            "sbowlID": info['bowler1ID'],
            "sbowlFName": info['bowler1FName'],
            "sbowlLName": info['bowler1LName'],
            "sbowlOvers": info['bowler1Overs'],
            "sbowlMaidens": info['bowler1Maidens'],
            "sbowlRuns": info['bowler1Runs'],
            "sbowlWickets": info['bowler1Wickets'],
            "sbowlEcon": info['bowler1Econ'],
            "nsbowlID": info['bowler2ID'],
            "nsbowlFName": info['bowler2FName'],
            "nsbowlLName": info['bowler2LName'],
            "nsbowlOvers": info['bowler2Overs'],
            "nsbowlMaidens": info['bowler2Maidens'],
            "nsbowlRuns": info['bowler2Runs'],
            "nsbowlWickets": info['bowler2Wickets'],
            "nsbowlEcon": info['bowler2Econ'],
            "lBat": info['lastBat'],
            "fbattingCard": json.loads(info['fbattingCard']),
            "fyetToBat": json.loads(info['fyetToBat']),
            "fbowlingCard": json.loads(info['fbowlingCard']),
            "sbattingCard": sbattingCard,
            "syetToBat": syetToBat,
            "sbowlingCard": sbowlingCard,
            "log": logText
        }
        conn.close()
        await websocket.send_text(json.dumps(liveInfo))
    elif info['matchPlayed']==-1:
        homeTeamInfo = cur.execute("SELECT name, color FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()
        homeTeamName = homeTeamInfo['name']
        homeTeamColor = homeTeamInfo['color']
        print(homeTeamColor)
        awayTeamInfo = cur.execute("SELECT name, color FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()
        awayTeamName = awayTeamInfo['name']
        awayTeamColor = awayTeamInfo['color']
        if info['batFirstID'] == info['homeTeamID']:
            batFirstName = homeTeamName
            batSecondID = info['awayTeamID']
            batSecondName = awayTeamName
        else:
            batFirstName = awayTeamName
            batSecondID = info['homeTeamID']
            batSecondName = homeTeamName
        if info['bFOvers'] == '19.6':
            info['bFOvers'] = '20.0'
        # Calculate Run Rate
        if info['bSOvers'] == None or info['bSOvers']=='YTB':
            info['bSOvers'] = 'YTB'
            info['bSRuns'] = 0
            info['bSWickets'] = 0
        if type(info['bFOvers']) == float:
                balls_faced = 0
        else:
                balls_faced = int(info['bFOvers'].split('.')[0]) * 6 + int(info['bFOvers'].split('.')[1])
        runs_scored = info['bFRuns']
        if balls_faced == 0:
                bfCRR = 0.00
        else:
                bfCRR = runs_scored / (int(balls_faced) / 6)
        if info['bSOvers'] == "YTB":
            bsCRR = 0.00
            bsRRR = 0.00
        else:
            try:
                balls_faced = int(info['bSOvers'].split('.')[0]) * 6 + int(info['bSOvers'].split('.')[1])
                balls_remaining = 120-balls_faced
                bsCRR = info['bSRuns'] / (balls_faced/6)
                if balls_remaining > 0:
                    bsRRR = (info['bFRuns'] - info['bSRuns']) / (balls_remaining/6)
                else:
                    bsRRR = 0
            except: 
                bsRRR = 0.00
                bsCRR = 0.00
                
        try:
            sbattingCard = json.loads(info['sbattingCard'])
            syetToBat = json.loads(info['syetToBat'])
        except:
            sbattingCard = None
            syetToBat = None
        try:
            fbattingCard = json.loads(info['fbattingCard'])
            fyetToBat = json.loads(info['fyetToBat'])
        except:
            fbattingCard = None
            fyetToBat = None
        # logText = json.loads(info['log'])
        logText = []
        try:
            for log in json.loads(info['log']):
                    logText.append(json.loads(log))
        except TypeError:
            logText = []
        liveInfo = {
            "status": "Live",
            "season": info['season'],
            "match": info['matchNo'],
            "homeTeam": homeTeamName,
            "homeTeamID": info['homeTeamID'],
            "homeTeamColor": homeTeamColor,
            "awayTeam": awayTeamName,
            "awayTeamID": info['awayTeamID'],
            "awayTeamColor": awayTeamColor,
            "bfName": batFirstName,
            "bfID": info['batFirstID'],
            "bsName": batSecondName,
            "bsID": batSecondID,
            "bfRuns": info['bFRuns'],
            "bfWickets": info['bFWickets'],
            "bfOvers": info['bFOvers'],
            "bfCRR": bfCRR,
            "bsRuns": info['bSRuns'],
            "bsWickets": info['bSWickets'],
            "bsOvers": info['bSOvers'],
            "bsCRR": bsCRR,
            "bsRRR": bsRRR,
            "overResults": info['overResults'],
            "ballEvent": info['ballEvent'],
            "ballText": info['ballText'],
            "currentOver": info['currentOver'],
            "currentBall": info['currentBall'],
            "strikeID": info['batter1ID'],
            "strikeFName": info['batter1FName'],
            "strikeLName": info['batter1LName'],
            "strikeRuns": info['batter1Runs'],
            "strikeBalls": info['batter1Balls'],
            "strikeFours": info['batter1Fours'],
            "strikeSixes": info['batter1Sixes'],
            "strikeSR": info['batter1SR'],
            "nstrikeID": info['batter2ID'],
            "nstrikeFName": info['batter2FName'],
            "nstrikeLName": info['batter2LName'],
            "nstrikeRuns": info['batter2Runs'],
            "nstrikeBalls": info['batter2Balls'],
            "nstrikeFours": info['batter2Fours'],
            "nstrikeSixes": info['batter2Sixes'],
            "nstrikeSR": info['batter2SR'],
            "sbowlID": info['bowler1ID'],
            "sbowlFName": info['bowler1FName'],
            "sbowlLName": info['bowler1LName'],
            "sbowlOvers": info['bowler1Overs'],
            "sbowlMaidens": info['bowler1Maidens'],
            "sbowlRuns": info['bowler1Runs'],
            "sbowlWickets": info['bowler1Wickets'],
            "sbowlEcon": info['bowler1Econ'],
            "nsbowlID": info['bowler2ID'],
            "nsbowlFName": info['bowler2FName'],
            "nsbowlLName": info['bowler2LName'],
            "nsbowlOvers": info['bowler2Overs'],
            "nsbowlMaidens": info['bowler2Maidens'],
            "nsbowlRuns": info['bowler2Runs'],
            "nsbowlWickets": info['bowler2Wickets'],
            "nsbowlEcon": info['bowler2Econ'],
            "lBat": info['lastBat'],
            "fbattingCard": fbattingCard,
            "fyetToBat": fyetToBat,
            "sbattingCard": sbattingCard,
            "syetToBat": syetToBat,
            "log": logText
        }
        await websocket.send_text(json.dumps(liveInfo))
        try:
            while True:
                await websocket.receive_text()
        except Exception as err:
            print(err)
            manager.disconnect(matchID, websocket)


    
    # await websocket.accept()
    # while True:
        # conn = sqlite3.connect(DB_NAME)
        # conn.row_factory = sqlite3.Row
        # cur = conn.cursor()
        # row = cur.execute(f"SELECT * FROM matches WHERE matchID = ?;", (matchID,)).fetchone()
        # if row:
        #     info = dict(row)
        #     print(info['matchPlayed'])
        #     if info['matchPlayed'] == 0:
        #         homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
        #         homeTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['homeTeamID'], ))
        #         awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
        #         awayTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['awayTeamID'], ))
        #         liveInfo = {
        #             "status": "Upcoming",
        #             "season": info['season'],
        #             "match": info['matchNo'],
        #             "homeTeam": homeTeamName,
        #             "homeTeamID": info['homeTeamID'],
        #             "homePlayers": homeTeamPlayers,
        #             "awayTeam": awayTeamName,
        #             "awayTeamID": info['awayTeamID'],
        #             "awayPlayers": awayTeamPlayers,
        #             "date": info['scheduledDate']
        #         }
        #     elif info['matchPlayed'] == -1:
        #         homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
        #         awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
        #         if info['batFirstID'] == info['homeTeamID']:
        #             batFirstName = homeTeamName
        #             batSecondID = info['awayTeamID']
        #             batSecondName = awayTeamName
        #         else:
        #             batFirstName = awayTeamName
        #             batSecondID = info['homeTeamID']
        #             batSecondName = homeTeamName
        #         if info['bFOvers'] == '19.6':
        #             info['bFOvers'] = '20.0'
        #         # Calculate Run Rate
        #         if type(info['bFOvers']) == float:
        #                 balls_faced = 0
        #         else:
        #                 balls_faced = int(info['bFOvers'].split('.')[0]) * 6 + int(info['bFOvers'].split('.')[1])
        #         runs_scored = info['bFRuns']
        #         if balls_faced == 0:
        #                 bfCRR = 0.00
        #         else:
        #                 bfCRR = runs_scored / (int(balls_faced) / 6)
        #         if info['bSOvers'] == "YTB":
        #             bsCRR = 0.00
        #             bsRRR = 0.00
        #         else:
        #             balls_faced = int(info['bSOvers'].split('.')[0]) * 6 + int(info['bSOvers'].split('.')[1])
        #             balls_remaining = 120-balls_faced
        #             bsCRR = info['bSRuns'] / (balls_faced/6)
        #             if balls_remaining > 0:
        #                 bsRRR = (info['bFRuns'] - info['bSRuns']) / (balls_remaining/6)
        #             else:
        #                 bsRRR = 0
        #         if info['sbattingCard'] == None:
        #             sbattingCard = None
        #             syetToBat = None
        #         else:
        #             sbattingCard = json.loads(info['sbattingCard'])
        #             syetToBat = json.loads(info['syetToBat'])
        #         # logText = json.loads(info['log'])
        #         logText = []
        #         for log in json.loads(info['log']):
        #                 logText.append(json.loads(log))
        #         liveInfo = {
        #             "status": "Live",
        #             "season": info['season'],
        #             "match": info['matchNo'],
        #             "homeTeam": homeTeamName,
        #             "homeTeamID": info['homeTeamID'],
        #             "awayTeam": awayTeamName,
        #             "awayTeamID": info['awayTeamID'],
        #             "bfName": batFirstName,
        #             "bfID": info['batFirstID'],
        #             "bsName": batSecondName,
        #             "bsID": batSecondID,
        #             "bfRuns": info['bFRuns'],
        #             "bfWickets": info['bFWickets'],
        #             "bfOvers": info['bFOvers'],
        #             "bfCRR": bfCRR,
        #             "bsRuns": info['bSRuns'],
        #             "bsWickets": info['bSWickets'],
        #             "bsOvers": info['bSOvers'],
        #             "bsCRR": bsCRR,
        #             "bsRRR": bsRRR,
        #             "overResults": info['overResults'],
        #             "ballEvent": info['ballEvent'],
        #             "ballText": info['ballText'],
        #             "currentOver": info['currentOver'],
        #             "currentBall": info['currentBall'],
        #             "strikeID": info['batter1ID'],
        #             "strikeFName": info['batter1FName'],
        #             "strikeLName": info['batter1LName'],
        #             "strikeRuns": info['batter1Runs'],
        #             "strikeBalls": info['batter1Balls'],
        #             "strikeFours": info['batter1Fours'],
        #             "strikeSixes": info['batter1Sixes'],
        #             "strikeSR": info['batter1SR'],
        #             "nstrikeID": info['batter2ID'],
        #             "nstrikeFName": info['batter2FName'],
        #             "nstrikeLName": info['batter2LName'],
        #             "nstrikeRuns": info['batter2Runs'],
        #             "nstrikeBalls": info['batter2Balls'],
        #             "nstrikeFours": info['batter2Fours'],
        #             "nstrikeSixes": info['batter2Sixes'],
        #             "nstrikeSR": info['batter2SR'],
        #             "sbowlID": info['bowler1ID'],
        #             "sbowlFName": info['bowler1FName'],
        #             "sbowlLName": info['bowler1LName'],
        #             "sbowlOvers": info['bowler1Overs'],
        #             "sbowlMaidens": info['bowler1Maidens'],
        #             "sbowlRuns": info['bowler1Runs'],
        #             "sbowlWickets": info['bowler1Wickets'],
        #             "sbowlEcon": info['bowler1Econ'],
        #             "nsbowlID": info['bowler2ID'],
        #             "nsbowlFName": info['bowler2FName'],
        #             "nsbowlLName": info['bowler2LName'],
        #             "nsbowlOvers": info['bowler2Overs'],
        #             "nsbowlMaidens": info['bowler2Maidens'],
        #             "nsbowlRuns": info['bowler2Runs'],
        #             "nsbowlWickets": info['bowler2Wickets'],
        #             "nsbowlEcon": info['bowler2Econ'],
        #             "lBat": info['lastBat'],
        #             "fbattingCard": json.loads(info['fbattingCard']),
        #             "fyetToBat": json.loads(info['fyetToBat']),
        #             "sbattingCard": sbattingCard,
        #             "syetToBat": syetToBat,
        #             "log": logText
        #         }
        #     elif info['matchPlayed'] == 1:
        #         # Needs refining to only necessary information
        #         homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
        #         awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
        #         if info['batFirstID'] == info['homeTeamID']:
        #             batFirstName = homeTeamName
        #             batSecondID = info['awayTeamID']
        #             batSecondName = awayTeamName
        #         else:
        #             batFirstName = awayTeamName
        #             batSecondID = info['homeTeamID']
        #             batSecondName = homeTeamName
        #         if info['bFOvers'] == '19.6':
        #             info['bFOvers'] = '20.0'
        #         # Calculate Run Rate
        #         if type(info['bFOvers']) == float:
        #                 balls_faced = 0
        #         else:
        #                 balls_faced = int(info['bFOvers'].split('.')[0]) * 6 + int(info['bFOvers'].split('.')[1])
        #         runs_scored = info['bFRuns']
        #         if balls_faced == 0:
        #                 bfCRR = 0.00
        #         else:
        #                 bfCRR = runs_scored / (int(balls_faced) / 6)
        #         if info['bSOvers'] == "YTB":
        #             bsCRR = 0.00
        #             bsRRR = 0.00
        #         else:
        #             balls_faced = int(info['bSOvers'].split('.')[0]) * 6 + int(info['bSOvers'].split('.')[1])
        #             balls_remaining = 120-balls_faced
        #             bsCRR = info['bSRuns'] / (balls_faced/6)
        #             if balls_remaining > 0:
        #                 bsRRR = (info['bFRuns'] - info['bSRuns']) / (balls_remaining/6)
        #             else:
        #                 bsRRR = 0
        #         if info['sbattingCard'] == None:
        #             sbattingCard = None
        #             syetToBat = None
        #         else:
        #             sbattingCard = json.loads(info['sbattingCard'])
        #             syetToBat = json.loads(info['syetToBat'])
        #         # logText = json.loads(info['log'])
        #         logText = []
        #         for log in json.loads(info['log']):
        #                 logText.append(json.loads(log))
        #         liveInfo = {
        #             "status": "played",
        #             "season": info['season'],
        #             "match": info['matchNo'],
        #             "homeTeam": homeTeamName,
        #             "homeTeamID": info['homeTeamID'],
        #             "awayTeam": awayTeamName,
        #             "awayTeamID": info['awayTeamID'],
        #             "bfName": batFirstName,
        #             "bfID": info['batFirstID'],
        #             "bsName": batSecondName,
        #             "bsID": batSecondID,
        #             "bfRuns": info['bFRuns'],
        #             "bfWickets": info['bFWickets'],
        #             "bfOvers": info['bFOvers'],
        #             "bfCRR": bfCRR,
        #             "bsRuns": info['bSRuns'],
        #             "bsWickets": info['bSWickets'],
        #             "bsOvers": info['bSOvers'],
        #             "bsCRR": bsCRR,
        #             "bsRRR": bsRRR,
        #             "overResults": info['overResults'],
        #             "ballEvent": info['ballEvent'],
        #             "ballText": info['ballText'],
        #             "currentOver": info['currentOver'],
        #             "currentBall": info['currentBall'],
        #             "strikeID": info['batter1ID'],
        #             "strikeFName": info['batter1FName'],
        #             "strikeLName": info['batter1LName'],
        #             "strikeRuns": info['batter1Runs'],
        #             "strikeBalls": info['batter1Balls'],
        #             "strikeFours": info['batter1Fours'],
        #             "strikeSixes": info['batter1Sixes'],
        #             "strikeSR": info['batter1SR'],
        #             "nstrikeID": info['batter2ID'],
        #             "nstrikeFName": info['batter2FName'],
        #             "nstrikeLName": info['batter2LName'],
        #             "nstrikeRuns": info['batter2Runs'],
        #             "nstrikeBalls": info['batter2Balls'],
        #             "nstrikeFours": info['batter2Fours'],
        #             "nstrikeSixes": info['batter2Sixes'],
        #             "nstrikeSR": info['batter2SR'],
        #             "sbowlID": info['bowler1ID'],
        #             "sbowlFName": info['bowler1FName'],
        #             "sbowlLName": info['bowler1LName'],
        #             "sbowlOvers": info['bowler1Overs'],
        #             "sbowlMaidens": info['bowler1Maidens'],
        #             "sbowlRuns": info['bowler1Runs'],
        #             "sbowlWickets": info['bowler1Wickets'],
        #             "sbowlEcon": info['bowler1Econ'],
        #             "nsbowlID": info['bowler2ID'],
        #             "nsbowlFName": info['bowler2FName'],
        #             "nsbowlLName": info['bowler2LName'],
        #             "nsbowlOvers": info['bowler2Overs'],
        #             "nsbowlMaidens": info['bowler2Maidens'],
        #             "nsbowlRuns": info['bowler2Runs'],
        #             "nsbowlWickets": info['bowler2Wickets'],
        #             "nsbowlEcon": info['bowler2Econ'],
        #             "lBat": info['lastBat'],
        #             "fbattingCard": json.loads(info['fbattingCard']),
        #             "fyetToBat": json.loads(info['fyetToBat']),
        #             "sbattingCard": sbattingCard,
        #             "syetToBat": syetToBat,
        #             "log": logText
        #         }
        # else:
        #     print("row not true")
        #     liveInfo = {"status": "No Match Found"}
        # # print(liveInfo)
        # print("Sending Info")
    #     await websocket.send_text(json.dumps(liveInfo))
    #     await asyncio.sleep(100)
