from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
from dotenv import load_dotenv
from os import getenv

load_dotenv()
BETS_DB = getenv("DBNAME")
USER_DB = getenv("ACC_DB")

router = APIRouter(prefix='/api/bets', tags=["Bets"])

class BetRequest(BaseModel):
    userID: int
    matchID: int
    teamID: int
    amount: int

@router.post("/place")
def place_bet(bet: BetRequest):
    bet_conn = sqlite3.connect(BETS_DB)
    bet_cur = bet_conn.cursor()

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()

    # does user have enough coins?
    row = user_cur.execute("SELECT coins FROM users WHERE userID=?", (bet.userID,)).fetchone()
    if not row:
        print(f"User {bet.userID} not found")
        return JSONResponse({"success": False, "error": "User Not Found"})
    if row[0] < bet.amount:
        print(f"User has {row[0]} coins, insufficient to bet {bet.amount}")
        return JSONResponse({"success": False, "error": "Not Enough Coins"})
    
    user_cur.execute("UPDATE users SET coins = coins - ? WHERE userID=?", (bet.amount, bet.userID,))

    bet_cur.execute("INSERT INTO bets(userID, matchID, teamID, amount) VALUES (?, ?, ?, ?)",
                    (bet.userID, bet.matchID, bet.teamID, bet.amount)
                    )
    
    user_conn.commit()
    bet_conn.commit()
    user_conn.close()
    bet_conn.close()
    print(f"User {bet.userID} has bet {bet.amount} on {bet.teamID} to win match {bet.matchID}")
    return JSONResponse({"success": True})

@router.get("/{userID}/{matchID}")
def get_bet_info(userID, matchID):
    conn = sqlite3.connect(BETS_DB)
    cur = conn.cursor()

    row = cur.execute("SELECT * FROM bets WHERE userID=? AND matchID=?", 
                (userID, matchID,)).fetchone()
    if row:
        teamID = row[3]
        amount = row[4]
        settled = row[5]
        payout = row[7]
        return JSONResponse({'bet': 1, 'teamID': teamID, 'amount': amount, 'settled': settled, 'payout': payout})
    else:
        return JSONResponse({'bet': 0})
