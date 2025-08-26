import sqlite3
from datetime import datetime
import random, json, time, sys
from math import ceil
import traceback, asyncio
from itertools import chain
from dotenv import load_dotenv
from os import getenv

from classes import Odds, rand, ConnectionManager

load_dotenv()
DB_NAME = getenv("DBNAME")
BALL_PAUSE = 4 # seconds (4)
OVER_PAUSE = 5 # seconds (5)
INNINGS_PAUSE = 10 # seconds (10)

async def ball_update(matchID):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute(f"SELECT * FROM matches WHERE matchID = ?;", (matchID,)).fetchone()
    if row:
        info = dict(row)
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
                bsCRR = info['bSRuns'] / ((balls_faced+1e-6)/6)
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
            try:
                for log in json.loads(info['log']):
                    logText.append(json.loads(log))
            except:
                logText = []
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
    else:
        liveInfo = {"status": "No Match Found"}
    # print(liveInfo)

    await manager.broadcast(matchID, liveInfo)
    # print("Sending Info")

def get_description(batter, bowler, ball):
    first_line = f"{bowler['fname']} {bowler['lname']} to {batter['fname']} {batter['lname']}\n"
    lineNo = random.randint(0, 59)
    if ball=='W':
        lineNo = random.randint(0, 99)
        fname='wicket.txt'
    elif ball=='+':
        fname='wideBall.txt'
    elif ball=='O':
        fname='noBall.txt'
    elif ball=='·':
        fname='dotBall.txt'
    elif ball=='1':
        fname='oneRun.txt'
    elif ball=='2':
        fname='twoRuns.txt'
    elif ball=='3':
        fname='threeRuns.txt'
    elif ball=='4':
        fname='fourRuns.txt'
    elif ball=='6':
        fname='sixRuns.txt'
    else:
        raise f"In get_description: ball {ball} not known"

    with open(f'ballOutcomes/{fname}') as fp:
        for i, line in enumerate(fp):
            if i==lineNo:
                desc = line
            elif i>lineNo:
                break
    try:
        desc = desc.replace("BATTER", f"{batter['fname']} {batter['lname']}")
        desc = desc.replace("BOWLER", f"{bowler['fname']} {bowler['lname']}")
    except UnboundLocalError:
        print(f"For ball {ball} and lineNo {lineNo}, no description generated.")
    print(desc)
    return desc

def create_live_db(conn, matchID, batTeamID, bfPlayers, bsPlayers):   
    fbattingCard = []
    fYTB = []
    batter1 = {}
    batter2 = {}
    for i, player in enumerate(bfPlayers):
        if i==0:
            fbattingCard.append({"ID":player['playerID'], "name":f"{player['fname']} {player['lname']}", "runs": 0, "balls": 0, "howOut": "Not Out"})
            batter1['ID'] = player['playerID']
            batter1['FName'] = player['fname']
            batter1['LName'] = player['lname']
        elif i==1:
            fbattingCard.append({"ID":player['playerID'], "name":f"{player['fname']} {player['lname']}", "runs": 0, "balls": 0, "howOut": "Not Out"})
            batter2['ID'] = player['playerID']
            batter2['FName'] = player['fname']
            batter2['LName'] = player['lname']
        else:
            fYTB.append({"ID": player['playerID'], "name": f"{player['fname']} {player['lname']}"})
    sbattingCard = []
    sYTB = []
    for i, player in enumerate(bsPlayers):
        if i<2:
            sbattingCard.append({"ID":player['playerID'], "name":f"{player['fname']} {player['lname']}", "runs": 0, "balls": 0, "howOut": "Not Out"})
        else:
            sYTB.append({"ID": player['playerID'], "name": f"{player['fname']} {player['lname']}"})
        if i==10:
            bowl1ID = player['playerID']
            bowl1FName = player['fname']
            bowl1LName = player['lname']
        elif i==9:
            bowl2ID = player['playerID']
            bowl2FName = player['fname']
            bowl2LName = player['lname']
    
    conn.cursor().execute("""
    UPDATE matches
    SET
        batFirstID = ?, 
        bFRuns = 0, 
        bFWickets = 0, 
        bFOvers = '0.0',
        bsOvers = 'YTB',
        batter1ID = ?,
        batter1FName = ?,
        batter1LName = ?,
        batter1Runs = 0,
        batter1Balls = 0,
        batter1Fours = 0,
        batter1Sixes = 0,
        batter1SR = 0,
        batter2ID = ?,
        batter2FName = ?,
        batter2LName = ?,
        batter2Runs = 0,
        batter2Balls = 0,
        batter2Fours = 0,
        batter2Sixes = 0,
        batter2SR = 0,
        bowler1ID = ?,
        bowler1FName = ?,
        bowler1LName = ?,
        bowler1Overs = 0,
        bowler1Maidens = 0,
        bowler1Runs = 0,
        bowler1Wickets = 0,
        bowler1Econ = 0.00,
        bowler2ID = ?,
        bowler2FName = ?,
        bowler2LName = ?,
        bowler2Overs = 0,
        bowler2Maidens = 0,
        bowler2Runs = 0,
        bowler2Wickets = 0,
        bowler2Econ = 0.00,
        currentBall = 0,
        currentOver = 0,
        fbattingCard = ?,
        fyetToBat = ?
    WHERE matchID = ?
    """, (batTeamID, batter1['ID'], batter1['FName'], batter1['LName'], batter2['ID'], batter2['FName'], batter2['LName'], bowl1ID, bowl1FName, bowl1LName, bowl2ID, bowl2FName, bowl2LName, json.dumps(fbattingCard), json.dumps(fYTB), matchID)
    )
    conn.commit()
    return matchID

def update_log(liveID, conn, label, desc, tag='ball-comm', value=None):
    full_log = []
    print(liveID)
    existing_log = dict(conn.cursor().execute("SELECT log FROM matches WHERE matchID=?", (liveID,)).fetchone())['log']
    if existing_log is not None:
        full_log = json.loads(existing_log)
    # label = f"{over}: {sbowler['fname']} {sbowler['lname']} to {striker['fname']} {striker['lname']}..."
    # desc = f"{desc}"
    full_log.append(json.dumps({"label": label, "value":value, "desc": desc.replace('\n', ''), "tag": tag}))
    conn.cursor().execute("""
        UPDATE matches
        SET log = ?
        WHERE matchID = ?
    """, (json.dumps(full_log), liveID))
    print(label)
    print(desc)
    conn.commit()

def update_live_state(liveID, conn, runs, wickets, over, target, over_results, event, desc, striker, non_striker, sbowler, nsbowler, result):
    if target == -1:
        bfRuns = runs
        bfWickets = wickets
        bfOvers = over
        bsOvers = 'YTB'
        print(f"Match {liveID}: {bfRuns} from {bfOvers}")
        conn.cursor().execute("""
            UPDATE matches
            SET 
                bFRuns = ?,
                bFWickets = ?,
                bFOvers = ?,
                bsOvers = ?
            WHERE 
                matchID==?
        """, (bfRuns, bfWickets, bfOvers, bsOvers, liveID))
        conn.commit()
    else:
        bfRuns = "bFRuns"
        bfWickets = "bFWickets"
        bfOvers = 'bFOvers'
        bsRuns = runs
        bsWickets = wickets
        bsOvers = over
        conn.cursor().execute("""
            UPDATE matches
            SET 
                bSRuns = ?,
                bSWickets = ?,
                bSOvers = ?
            WHERE 
                matchID==?
        """, (bsRuns, bsWickets, bsOvers, liveID))
        conn.commit()
    
    currentOver, currentBall = over.split('.')

    conn.cursor().execute("""
        UPDATE matches
        SET
            overResults = ?,
            ballEvent = ?,
            ballText = ?,
            currentOver = ?,
            currentBall = ?
        WHERE
            matchID == ?
    """, (over_results, event, desc, currentOver, currentBall, liveID))
    conn.commit()

    if striker['B'] > 0:
        striker_SR = striker['RS'] / striker['B'] * 100
    else:
        striker_SR = 0
    conn.cursor().execute("""
        UPDATE matches
        SET
            batter1ID = ?,
            batter1FName = ?,
            batter1LName = ?,
            batter1Runs = ?,
            batter1Balls = ?,
            batter1Fours = ?,
            batter1Sixes = ?,
            batter1SR = ?
        WHERE
            matchID == ?
    """, (striker['playerID'], striker['fname'], striker['lname'], striker['RS'], striker['B'], striker['4s'], striker['6s'], striker_SR, liveID))
    conn.commit()    
    
    if non_striker['B'] > 0:
        nstriker_SR = non_striker['RS'] / non_striker['B'] * 100
    else:
        nstriker_SR = 0
    conn.cursor().execute("""
        UPDATE matches
        SET
            batter2ID = ?,
            batter2FName = ?,
            batter2LName = ?,
            batter2Runs = ?,
            batter2Balls = ?,
            batter2Fours = ?,
            batter2Sixes = ?,
            batter2SR = ?
        WHERE
            matchID == ?
    """, (non_striker['playerID'], non_striker['fname'], non_striker['lname'], non_striker['RS'], non_striker['B'], non_striker['4s'], non_striker['6s'], nstriker_SR, liveID))
    conn.commit()    

    if sbowler['O'] == 0.0:
        sbowlerEcon = 0.00
    else:
        oversBowled, ballsBowled = str(sbowler['O']).split('.')
        sbowlerEcon = sbowler['RC'] / ((6*int(oversBowled) + int(ballsBowled[0]))/6)

    conn.cursor().execute("""
        UPDATE matches
        SET
            bowler1ID = ?,
            bowler1FName = ?,
            bowler1LName = ?,
            bowler1Overs = ?,
            bowler1Maidens = ?,
            bowler1Runs = ?,
            bowler1Wickets = ?,
            bowler1Econ = ?
        WHERE
            matchID==?
    """, (sbowler['playerID'], sbowler['fname'], sbowler['lname'], sbowler['O'], sbowler['M'], sbowler['RC'], sbowler['W'], sbowlerEcon, liveID))
    conn.commit()

    if nsbowler['O'] == 0.0:
        nsbowlerEcon = 0.00
    else:
        oversBowled, ballsBowled = str(nsbowler['O']).split('.')
        nsbowlerEcon = nsbowler['RC'] / ((6*int(oversBowled) + int(ballsBowled[0]))/6)

    conn.cursor().execute("""
        UPDATE matches
        SET
            bowler2ID = ?,
            bowler2FName = ?,
            bowler2LName = ?,
            bowler2Overs = ?,
            bowler2Maidens = ?,
            bowler2Runs = ?,
            bowler2Wickets = ?,
            bowler2Econ = ?
        WHERE
            matchID==?
    """, (nsbowler['playerID'], nsbowler['fname'], nsbowler['lname'], nsbowler['O'], nsbowler['M'], nsbowler['RC'], nsbowler['W'], nsbowlerEcon, liveID))
    conn.commit()

    # Append to log
    # existing_log = dict(conn.cursor().execute("SELECT log FROM matches WHERE matchID=?", (liveID)).fetchone())['log']
    label = f"{over}: {sbowler['fname']} {sbowler['lname']} to {striker['fname']} {striker['lname']}..."
    desc = f"{desc}"
    update_log(liveID, conn, label, desc, value=result)
    # [{"BallLabel": "3.2: Sutton Bishop to Jayden Hotdogfingers...", "BallDesc": "WICKET: A sharp catch in the followthrough!"}]

def update_how_out(liveID, conn, desc, batter, bowler, delivery):
    dismissal_type = desc.split('! | ')[0]
    if dismissal_type.lower() == "caught":
        dismissal_text = f"Caught, Bowled {bowler['fname'][0]}. {bowler['lname']}"
    elif dismissal_type.lower() == "bowled":
        dismissal_text = f"Bowled {bowler['fname'][0]}. {bowler['lname']}"
    elif dismissal_type.lower() == "lbw":
        dismissal_text = f"LBW {bowler['fname'][0]}. {bowler['lname']}"
    elif dismissal_type.lower() == 'run out':
        dismissal_text = f"Run Out"
    elif dismissal_type.lower() == "stumped":
        dismissal_text = f"Stumped, Bowled {bowler['fname'][0]}. {bowler['lname']}"
    else:
        raise f"Unknown dismissal {dismissal_type}"
    last_wicket_text = f"Last Bat: {batter['fname']} {batter['lname']} {batter['RS']} ({batter['B']}). {dismissal_text}"
    print(last_wicket_text)
    conn.cursor().execute("""
        UPDATE matches
        SET lastBat = ?
        WHERE matchID==?
    """, (last_wicket_text, liveID))
    conn.commit()
    batter['howOut'] = dismissal_text

def update_scorecard(liveID, conn, batting_team, target):
    battingCard = []
    yet_to_bat = []
    for player in batting_team:
        try:
            player['B']
            battingCard.append({
                "ID": player['playerID'],
                "name": f"{player['fname']} {player['lname']}",
                "runs": player['RS'],
                "balls": player['B'],
                "howOut": player['howOut']
            })
        except KeyError:
            yet_to_bat.append({
                "ID": player['playerID'],
                "name": f"{player['fname']} {player['lname']}"
            })
    if target < 0:
        conn.cursor().execute("""
            UPDATE matches
            SET 
                fbattingCard = ?,
                fyetToBat = ?
            WHERE matchID = ?
        """, (json.dumps(battingCard), json.dumps(yet_to_bat), liveID))
        conn.commit()
    else:
        conn.cursor().execute("""
            UPDATE matches
            SET 
                sbattingCard = ?,
                syetToBat = ?
            WHERE matchID = ?
        """, (json.dumps(battingCard), json.dumps(yet_to_bat), liveID))
        conn.commit()
    return

def get_outcome(batter, bowler):
    ball_odds = random.uniform(0, 1)
    bat_stat = [
        rand(batter['power']),
        rand(batter['technique']),
        rand(batter['aggression']),
        rand(batter['patience'])
    ]
    bowl_stat = (
        rand(bowler['pace']),
        rand(bowler['movement']),
        rand(bowler['accuracy']),
        rand(bowler['length'])
    )
    odds = Odds(bat_stat, bowl_stat)
    if ball_odds < odds.run_total(odds.wicket):
        batter['B'] += 1
        # bowler['O'] += 0.1
        bowler['W'] += 1
        return 0, "W", "WICKET"
    elif ball_odds < odds.run_total(odds.wide):
        bowler['RC'] += 1
        return 1, "+", "Wide"
    elif ball_odds < odds.run_total(odds.noBall):
        bowler['RC'] += 1
        return 1, "O", "No Ball"
    elif ball_odds < odds.run_total(odds.dotBall):
        batter['B'] += 1
        # bowler['O'] += 0.1
        return 0, "·", "Dot"
    elif ball_odds < odds.run_total(odds.oneRun):
        batter['B'] += 1
        batter['RS'] += 1
        # bowler['O'] += 0.1
        bowler['RC'] += 1
        return 1, "1", "Single"
    elif ball_odds < odds.run_total(odds.twoRuns):
        batter['B'] += 1
        batter['RS'] += 2
        # bowler['O'] += 0.1
        bowler['RC'] += 2
        return 2, "2", "Double"
    elif ball_odds < odds.run_total(odds.threeRuns):
        batter['B'] += 1
        batter['RS'] += 3
        # bowler['O'] += 0.1
        bowler['RC'] += 3
        return 3, "3", "Three"
    elif ball_odds < odds.run_total(odds.fourRuns):
        batter['B'] += 1
        batter['RS'] += 4
        batter['4s'] += 1
        # bowler['O'] += 0.1
        bowler['RC'] += 4
        return 4, "4", "FOUR"
    else:
        batter['B'] += 1
        batter['RS'] += 6
        batter['6s'] += 1
        # bowler['O'] += 0.1
        bowler['RC'] += 6
        return 6, "6", "SIX"

async def simulate_innings(liveID, batting_team, batTeamID, bowling_team, bowlTeamID, max_overs=20, target=-1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    wickets = 0
    total_runs = 0
    balls = 0
    over = 0
    striker_index = 0
    batting_team[striker_index]['RS'] = 0
    batting_team[striker_index]['B'] = 0
    batting_team[striker_index]['4s'] = 0
    batting_team[striker_index]['6s'] = 0
    batting_team[striker_index]['howOut'] = "Not Out"
    non_striker_index = 1
    batting_team[non_striker_index]['RS'] = 0
    batting_team[non_striker_index]['B'] = 0
    batting_team[non_striker_index]['4s'] = 0
    batting_team[non_striker_index]['6s'] = 0
    batting_team[non_striker_index]['howOut'] = "Not Out"
    sbowler_index = 10
    nsbowler_index = 9
    bowling_team[sbowler_index]['O'] = 0.0
    bowling_team[sbowler_index]['M'] = 0
    bowling_team[sbowler_index]['RC'] = 0
    bowling_team[sbowler_index]['W'] = 0
    bowling_team[nsbowler_index]['O'] = 0.0
    bowling_team[nsbowler_index]['M'] = 0
    bowling_team[nsbowler_index]['RC'] = 0
    bowling_team[nsbowler_index]['W'] = 0
    log = []
    matchOver = False
    while over < max_overs and wickets < 10 and not matchOver:
        sbowler = bowling_team[sbowler_index]
        nsbowler = bowling_team[nsbowler_index]
        over_results = ''
        ball_in_over = 0
        runs_this_over = 0
        wickets_this_over = 0
        while ball_in_over < 6:
            batter = batting_team[striker_index]
            non_striker = batting_team[non_striker_index]
            runs, result, event = get_outcome(batter, sbowler)
            runs_this_over += runs
            desc = get_description(batter, sbowler, result)

            over_results += result+' '
            log.append({
                "over": round(over + ball_in_over / 6.0, 1),
                "batterID": batter['playerID'],
                "bowlerID": sbowler['playerID'],
                "runs": runs,
                "event": event,
                "description": desc
            })
            if not (event == "Wide" or event=="No Ball"):
                ball_in_over += 1
                balls += 1
                sbowler['O'] += 0.1
            if event == "WICKET":
                update_how_out(liveID, conn, desc, batter, sbowler, f"{over}.{ball_in_over-1}")
                wickets += 1
                wickets_this_over += 1
                if wickets < 10:
                    striker_index = max(striker_index, non_striker_index) + 1
                    batting_team[striker_index]['RS'] = 0
                    batting_team[striker_index]['B'] = 0
                    batting_team[striker_index]['4s'] = 0
                    batting_team[striker_index]['6s'] = 0
                    batting_team[striker_index]['howOut'] = "Not Out"
            else:
                total_runs += runs
                if runs % 2 == 1:
                    striker_index, non_striker_index = non_striker_index, striker_index
            update_live_state(liveID, conn, total_runs, wickets, f"{over}.{ball_in_over}", target, over_results, event, desc, batter, non_striker, sbowler, nsbowler, result)
            update_scorecard(liveID, conn, batting_team, target)
            # asyncio.run(ball_update(liveID))
            await ball_update(liveID)
            # time.sleep(BALL_PAUSE)
            await asyncio.sleep(BALL_PAUSE)
            if wickets >= 10:
                break
            if target > 0 and total_runs > target:
                matchOver = True
                break

            
        sbowler['O'] = ceil(sbowler['O'])+0.0
        # if ['1', '2', '3', '4', '6', '+', 'O'] not in over_results:
        if not any(result in over_results for result in ['1', '2', '3', '4', '6', '+', 'O']):
            sbowler['M'] += 1
        
        striker_index, non_striker_index = non_striker_index, striker_index
        sbowler_index, nsbowler_index = nsbowler_index, sbowler_index
        if bowling_team[sbowler_index]['O'] >= 2.0:
            sbowler_index -= 2
            if sbowler_index < 0:
                sbowler_index = 10
            try:
                bowling_team[sbowler_index]['O'] += 0
            except KeyError:
                bowling_team[sbowler_index]['O'] = 0
                bowling_team[sbowler_index]['M'] = 0
                bowling_team[sbowler_index]['RC'] = 0
                bowling_team[sbowler_index]['W'] = 0
        label = f'End of Over {over+1}.'
        desc = f'Runs Scored: {runs_this_over}, Wickets Taken: {wickets_this_over}'
        over += 1
        update_log(liveID, conn, label, desc, tag='over-comm')
        # asyncio.run(ball_update(liveID))
        await ball_update(liveID)
        # time.sleep(OVER_PAUSE)
        await asyncio.sleep(OVER_PAUSE)

    return {
        "runs": total_runs,
        "wickets": wickets,
        "balls": balls,
        "log": log
    }

def update_end_of_innings(liveID, conn, innings_desc, innings):
    conn.cursor().execute("""
        UPDATE matches
        SET 
            ballText = ?,
            ballEvent = ?
        WHERE matchID = ?
    """, (innings_desc, "End of Innings", liveID))
    conn.commit()

    asyncio.create_task(ball_update(liveID))

def update_career_stats(conn, matchID, home_players, away_players):
    all_players = list(chain(*[home_players, away_players]))
    for player in all_players:
        # print(player)
        player['matches_played'] += 1
        try: 
            player['balls_faced'] += player['B']
            player['innings_batted'] += 1
            player['runs_scored'] += player['RS']
            if player['RS'] > int(player['highest_score'].replace('*', '')):
                player['highest_score'] = str(player['RS'])
                player['highest_balls_faced'] = player['B']
                if player['howOut'] == 'Not Out':
                    player['highest_score'] += '*'
                player['best_bat_ID'] = matchID
            elif player['RS'] == int(player['highest_score'].replace('*', '')):
                if (player['howOut'] == 'Not Out') and ('*' not in player['highest_score']):
                    player['highest_score'] = str(player['RS'])+'*'
                    player['highest_balls_faced'] = player['B']
                    player['best_bat_ID'] = matchID
                elif player['B'] < player['highest_balls_faced']:
                    player['highest_score'] = str(player['RS'])
                    player['highest_balls_faced'] = player['B']
                    player['best_bat_ID'] = matchID
            if player['howOut'] == 'Not Out':
                player['not_outs'] += 1
            if player['RS'] >= 100:
                player['hundreds'] += 1
            elif player['RS'] >= 50:
                player['fifties'] += 1
            player['fours'] += player['4s']
            player['sixes'] += player['6s']
        except Exception:
            # traceback.print_exc()
            pass
        try:
            player['overs_bowled'] = str(player['O'])
            if '.' not in player['overs_bowled']:
                player['overs_bowled'] = player['overs_bowled'] + '.0'
            player['innings_bowled'] += 1
            if player['RC'] == 0:
                player['maidens_bowled'] += 1
            player['runs_conceded'] += player['RC']
            player['wickets_taken'] += player['W']
            if player['W'] > player['best_figures_wickets']:
                player['best_figures_wickets'] = player['W']
                player['best_figures_runs'] = player['RC']
                player['best_bowl_ID'] = matchID
            if player['W'] == player['best_figures_wickets']:
                if player['RC'] < player['best_figures_runs']:
                    player['best_figures_wickets'] = player['W']
                    player['best_figures_runs'] = player['RC']
                    player['best_bowl_ID'] = matchID
        except Exception:
            # traceback.print_exc()
            pass
        # print(player)
        conn.cursor().execute("""
            UPDATE player_career_stats
            SET
                matches_played = ?,
                innings_batted = ?,
                runs_scored = ?,
                balls_faced = ?,
                highest_score = ?,
                highest_balls_faced = ?,
                best_bat_id = ?,
                not_outs = ?,
                fifties = ?,
                hundreds = ?,
                fours = ?,
                sixes = ?,
                innings_bowled = ?,
                overs_bowled = ?,
                maidens_bowled = ?,
                runs_conceded = ?,
                wickets_taken = ?,
                best_figures_wickets = ?,
                best_figures_runs = ?,
                best_bowl_id = ?
            WHERE
                playerID = ?
        """, (
            player['matches_played'],
            player['innings_batted'],
            player['runs_scored'],
            player['balls_faced'],
            player['highest_score'],
            player['highest_balls_faced'],
            player['best_bat_ID'],
            player['not_outs'],
            player['fifties'],
            player['hundreds'],
            player['fours'],
            player['sixes'],
            player['innings_bowled'],
            player['overs_bowled'],
            player['maidens_bowled'],
            player['runs_conceded'],
            player['wickets_taken'],
            player['best_figures_wickets'],
            player['best_figures_runs'],
            player['best_bowl_ID'],
            player['playerID']
        ))
    conn.commit()

async def simulate_match(matchID, conn_man):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    global manager
    manager = conn_man
    print("match_sim:", manager, manager.active_connections)
    print("Finding info for match", matchID)
    #* Fetch Match Info
    cur.execute("SELECT * FROM matches WHERE matchID = ?", (matchID,))
    match = cur.fetchone()
    print(match['matchPlayed'])
    if not match or match['matchPlayed'] == 1:
        print("Match already played or doesn't exist")
        return

    cur.execute("UPDATE matches SET matchPlayed = -1 WHERE matchID = ?", (matchID,))
    
    def get_team_name(teamID):
        cur.execute('''
        SELECT name FROM teams WHERE teamID = ?
        ''', (teamID, ))
        name = cur.fetchone()
        return name['name']
    
    homeTeamID = match['homeTeamID']
    awayTeamID = match['awayTeamID']

    homeTeamName = get_team_name(match['homeTeamID'])
    awayTeamName = get_team_name(match['awayTeamID'])
    
    season_number = match['season']
    match_number = match['matchNo']
    print(f"""Season {season_number} Match {match_number}
            {homeTeamName} vs {awayTeamName}""")

    def fetch_players(teamID):
        cur.execute('''
            SELECT p.*, s.* FROM players p
            LEFT JOIN player_career_stats s ON p.playerID = s.playerID
            INNER JOIN player_teams pt ON pt.playerID = p.playerID
            WHERE pt.teamID = ? AND pt.end_date IS NULL
        ''', (teamID, ))
        return [dict(row) for row in cur.fetchall()]

    home_players = fetch_players(homeTeamID)
    away_players = fetch_players(awayTeamID)

    #* Set batting order (currently random)
    random.shuffle(home_players)
    random.shuffle(away_players)

    #* Do the toss (currently, home team bats first)
    print(f"{homeTeamName} will bat first.")
    batTeamID = homeTeamID
    batPlayers = home_players
    bowlTeamID = awayTeamID
    bowlPlayers = away_players

    liveID = create_live_db(conn, matchID, batTeamID, batPlayers, bowlPlayers)
    await ball_update(liveID)
    # time.sleep(INNINGS_PAUSE)
    await asyncio.sleep(INNINGS_PAUSE)

    #* Simulate the Innings
    first_innings = await simulate_innings(liveID, home_players, homeTeamID, away_players, awayTeamID)
    innings_desc = f"{homeTeamName} finish on {first_innings['runs']} - {first_innings['wickets']} from {first_innings['balls']} balls"
    print(innings_desc)
    update_end_of_innings(liveID, conn, innings_desc, 1)
    update_log(liveID, conn, "End of Innings", innings_desc, tag='innings-comm')
    # time.sleep(INNINGS_PAUSE)
    await asyncio.sleep(INNINGS_PAUSE)
    second_innings = await simulate_innings(liveID, away_players, awayTeamID, home_players, homeTeamID, target=first_innings['runs']+1)
    innings_desc = f"{awayTeamName} finish on {second_innings['runs']} - {second_innings['wickets']} from {second_innings['balls']} balls"
    print(innings_desc)
    update_end_of_innings(liveID, conn, innings_desc, 2)

    #* Determine Winner
    if first_innings['runs'] > second_innings['runs']:
        result = f'{homeTeamName} win!'
        print(f"{homeTeamName} win!")
        update_log(liveID, conn, f"Match Over!", f"{homeTeamName} win!", tag='result-comm')
        cur.execute('''
            UPDATE matches SET
                ballEvent = 'Match Over',
                ballText = ?
            WHERE matchID = ?
        ''', (f"{homeTeamName} win!", liveID))
        cur.execute('''
            UPDATE teams SET
                gamesPlayed = gamesPlayed + 1,
                gamesWon = gamesWon + 1,
                oversFaced = oversFaced + ?,
                runsScored = runsScored + ?,
                oversBowled = oversBowled + ?,
                runsConceded = runsConceded + ?
            WHERE teamID = ?
            ''', 
            (first_innings['balls']//6, first_innings['runs'], second_innings['balls']//6, second_innings['runs'], homeTeamID)
        )

        cur.execute('''
        UPDATE teams SET
            gamesPlayed = gamesPlayed + 1,
            gamesLost = gamesLost + 1,
            oversFaced = oversFaced + ?,
            runsScored = runsScored + ?,
            oversBowled = oversBowled + ?,
            runsConceded = runsConceded + ?
        WHERE teamID = ?
        ''', 
        (second_innings['balls']//6, second_innings['runs'], first_innings['balls']//6, first_innings['runs'], awayTeamID)
        )
    elif second_innings['runs'] > first_innings['runs']:
        result = f'{awayTeamName} win!'
        print(f"{awayTeamName} win!")
        update_log(liveID, conn, f"Match Over!", f"{awayTeamName} win!", tag='result-comm')
        cur.execute('''
            UPDATE matches SET
                ballEvent = 'Match Over',
                ballText = ?
            WHERE matchID = ?
        ''', (f'{awayTeamName} win!', liveID))

        cur.execute('''
            UPDATE teams SET
                gamesPlayed = gamesPlayed + 1,
                gamesLost = gamesLost + 1,
                oversFaced = oversFaced + ?,
                runsScored = runsScored + ?,
                oversBowled = oversBowled + ?,
                runsConceded = runsConceded + ?
            WHERE teamID = ?
            ''', 
            (first_innings['balls']//6, first_innings['runs'], second_innings['balls']//6, second_innings['runs'], homeTeamID)
        )
        cur.execute('''
        UPDATE teams SET
            gamesPlayed = gamesPlayed + 1,
            gamesWon = gamesWon + 1,
            oversFaced = oversFaced + ?,
            runsScored = runsScored + ?,
            oversBowled = oversBowled + ?,
            runsConceded = runsConceded + ?
        WHERE teamID = ?
        ''', 
        (second_innings['balls']//6, second_innings['runs'], first_innings['balls']//6, first_innings['runs'], awayTeamID)
        )
    else:
        result = 'Tied game!'
        print("The game is a tie!")
        update_log(liveID, conn, f"Match Over!", f"It's a tie!", tag='result-comm')
        cur.execute('''
            UPDATE teams SET
                gamesPlayed = gamesPlayed + 1,
                gamesTied = gamesTied + 1,
                oversFaced = oversFaced + ?,
                runsScored = runsScored + ?,
                oversBowled = oversBowled + ?,
                runsConceded = runsConceded + ?
            WHERE teamID = ?
            ''', 
            (first_innings['balls']//6, first_innings['runs'], second_innings['balls']//6, second_innings['runs'], homeTeamID)
        )
        cur.execute('''
        UPDATE teams SET
            gamesPlayed = gamesPlayed + 1,
            gamesTied = gamesTied + 1,
            oversFaced = oversFaced + ?,
            runsScored = runsScored + ?,
            oversBowled = oversBowled + ?,
            runsConceded = runsConceded + ?
        WHERE teamID = ?
        ''', 
        (second_innings['balls']//6, second_innings['runs'], first_innings['balls']//6, first_innings['runs'], awayTeamID)
        )
    
    update_career_stats(conn, matchID, home_players, away_players)

    #* Store match result

    cur.execute('''
        UPDATE matches SET
                matchPlayed = 1,
                result = ?,
                homeScore = ?,
                awayScore = ?
        WHERE matchID = ?
    ''', (
        result, first_innings['runs'], second_innings['runs'], matchID
    ))
    # asyncio.run(ball_update(matchID))
    await ball_update(matchID)
    conn.commit()
    conn.close()



    print(f"Match {matchID} Simulated.")

def run_scheduled_simulations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Fetch unplayed matches scheduled <= now
    cursor.execute(
        """
        SELECT matchID, homeTeamID, awayTeamID FROM matches
        WHERE matchPlayed = 0 AND scheduledDate <= ?
        ORDER BY scheduledDate ASC
    """,
        (now,),
    )
    matches_to_play = cursor.fetchall()

    for matchID, homeTeamID, awayTeamID in matches_to_play:
        
        result = simulate_match(matchID)

        # Update match with result - for now just store result as text columns (add fields to your matches table accordingly)
        # You might want a match_results table for detailed stats instead
        cursor.execute(
            """
            UPDATE matches SET
                matchPlayed = 1,
                result = ?,
                homeScore = ?,
                awayScore = ?
            WHERE matchID = ?
        """,
            (result["result"], result["home_score"], result["away_score"], matchID),
        )

        print(
            f"Simulated Match {matchID}: Home {homeTeamID} vs Away {awayTeamID} — Result: {result['result']}"
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # run_scheduled_simulations()
    if len(sys.argv) > 1:
        matchID = sys.argv[1]
    else:
        matchID = 0

    manager = ConnectionManager()
    asyncio.run(simulate_match(matchID, manager))
