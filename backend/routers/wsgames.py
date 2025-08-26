from fastapi import FastAPI, WebSocket
from models import fetch_all, fetch_one
import sqlite3, json
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")

app = FastAPI()

@app.websocket("/ws/game/{gameID}")
async def websocket_endpoint(websocket: WebSocket, gameID: int):
    await websocket.accept()
    while True:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute(f"SELECT * FROM matches WHERE matchID = ?;", (matchID,)).fetchone()
        print("fetching Match", matchID)
        if row:
            info = dict(row)
            print(info['matchPlayed'])
            if info['matchPlayed'] == 0:
                homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
                homeTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['homeTeamID'], ))
                awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
                awayTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['awayTeamID'], ))
                liveInfo = {
                    "status": "Upcoming",
                    "season": info['season'],
                    "match": info['matchNo'],
                    "homeTeam": homeTeamName,
                    "homeTeamID": info['homeTeamID'],
                    "homePlayers": homeTeamPlayers,
                    "awayTeam": awayTeamName,
                    "awayTeamID": info['awayTeamID'],
                    "awayPlayers": awayTeamPlayers,
                    "date": info['scheduledDate']
                }
            elif info['matchPlayed'] == -1:
                homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
                awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
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
                else:
                    sbattingCard = json.loads(info['sbattingCard'])
                    syetToBat = json.loads(info['syetToBat'])
                # logText = json.loads(info['log'])
                logText = []
                for log in json.loads(info['log']):
                        logText.append(json.loads(log))
                liveInfo = {
                    "status": "Live",
                    "season": info['season'],
                    "match": info['matchNo'],
                    "homeTeam": homeTeamName,
                    "homeTeamID": info['homeTeamID'],
                    "awayTeam": awayTeamName,
                    "awayTeamID": info['awayTeamID'],
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
                    "sbattingCard": sbattingCard,
                    "syetToBat": syetToBat,
                    "log": logText
                }
            elif info['matchPlayed'] == 1:
                # Needs refining to only necessary information
                homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
                awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
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
                else:
                    sbattingCard = json.loads(info['sbattingCard'])
                    syetToBat = json.loads(info['syetToBat'])
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
                    "awayTeam": awayTeamName,
                    "awayTeamID": info['awayTeamID'],
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
                    "sbattingCard": sbattingCard,
                    "syetToBat": syetToBat,
                    "log": logText
                }
                return liveInfo
        else:
            liveInfo = {"status": "No Match Found"}
        await websocket.send_text(json.dumps(liveInfo))
        await asyncio.sleep(1)


router = APIRouter(prefix="/game", tags=["Game"])

@router.get("/{matchID}")
def get_live_match(matchID: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute(f"SELECT * FROM matches WHERE matchID = ?;", (matchID,)).fetchone()
    print("fetching Match", matchID)
    if row:
        info = dict(row)
        print(info['matchPlayed'])
        if info['matchPlayed'] == 0:
            homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
            homeTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['homeTeamID'], ))
            awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
            awayTeamPlayers = fetch_all("SELECT p.fname, p.lname, p.playerID FROM players p JOIN player_teams pt ON p.playerID = pt.playerID WHERE pt.teamID = ?", (info['awayTeamID'], ))
            liveInfo = {
                "status": "Upcoming",
                "season": info['season'],
                "match": info['matchNo'],
                "homeTeam": homeTeamName,
                "homeTeamID": info['homeTeamID'],
                "homePlayers": homeTeamPlayers,
                "awayTeam": awayTeamName,
                "awayTeamID": info['awayTeamID'],
                "awayPlayers": awayTeamPlayers,
                "date": info['scheduledDate']
            }
            return liveInfo
        elif info['matchPlayed'] == -1:
            homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
            awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
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
            else:
                sbattingCard = json.loads(info['sbattingCard'])
                syetToBat = json.loads(info['syetToBat'])
            # logText = json.loads(info['log'])
            logText = []
            for log in json.loads(info['log']):
                    logText.append(json.loads(log))
            liveInfo = {
                "status": "Live",
                "season": info['season'],
                "match": info['matchNo'],
                "homeTeam": homeTeamName,
                "homeTeamID": info['homeTeamID'],
                "awayTeam": awayTeamName,
                "awayTeamID": info['awayTeamID'],
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
                "sbattingCard": sbattingCard,
                "syetToBat": syetToBat,
                "log": logText
            }
            return liveInfo
        elif info['matchPlayed'] == 1:
            # Needs refining to only necessary information
            homeTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?;", (int(info['homeTeamID']),)).fetchone()['name']
            awayTeamName = cur.execute("SELECT name FROM teams WHERE teamID = ?", (info['awayTeamID'],)).fetchone()['name']
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
            else:
                sbattingCard = json.loads(info['sbattingCard'])
                syetToBat = json.loads(info['syetToBat'])
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
                "awayTeam": awayTeamName,
                "awayTeamID": info['awayTeamID'],
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
                "sbattingCard": sbattingCard,
                "syetToBat": syetToBat,
                "log": logText
            }
            print(liveInfo)
            return liveInfo
    return {"status": "No Live Match"}