from sqlalchemy import JSON
from fastapi import APIRouter, Form, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from models import fetch_all, fetch_one
from typing import Annotated
import sqlite3, json
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv()
ACC_DB = getenv("ACC_DB")

router = APIRouter(prefix="/api/account", tags=["Account"])
ph = PasswordHasher()

@router.post("/login")
def login(uname: Annotated[str, Form()], pswd: Annotated[str, Form()]):
        conn = sqlite3.connect(ACC_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE username = ?;", (uname,)).fetchone()
        if row is None:
                print(f"Username {uname} not found.")
                return JSONResponse(content={"logged-in": 0, 'error':"Username not found"}, status_code=401)
        else:
                userInfo = dict(row)
                try:
                        ph.verify(userInfo['hashedPassword'], pswd)
                        print(f"User {uname} logged in.")
                        response = JSONResponse(content={'logged-in': 1, "username": uname})
                        response.set_cookie(
                                key='session',
                                value=uname,
                                httponly=True,
                                secure=True,
                                samesite='lax'
                        )
                        return response
                except VerifyMismatchError:
                        print(f"User {uname} log-in failed. Password incorrect")
                        return JSONResponse(content={"logged-in": 0, 'error': 'Incorrect Password'}, status_code=401)

@router.post("/create")
def create_login(uname: Annotated[str, Form()], pswd: Annotated[str, Form()], conf_pswd: Annotated[str, Form()]):
        if pswd != conf_pswd:
                print("Password Don't Match")
                return {"account-created": 0, "error": "Passwords do not match"}
        else:
                phash = ph.hash(pswd)
                
                conn=sqlite3.connect(ACC_DB)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                try:
                        cur.execute("""
                                INSERT INTO
                                        users (username, hashedPassword)
                                VALUES
                                        (?, ?);
                        """, (uname, phash))
                except sqlite3.IntegrityError:
                        print("Username Taken")
                        conn.close()
                        return {"account-created": 0, "error": "Username already exists"}
                conn.commit()
                conn.close()
                return {"account-created": 1}
        
@router.get("/detail/{userID}")
def get_user_info(userID):
        conn = sqlite3.connect(ACC_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE userID=?;", (userID,)).fetchone()
        return JSONResponse(content={"ID": row['userID'], "uname": row['username'], "favTeam": row['favTeam'], "coins": row['coins']}, status_code=200)

@router.get("/me")
def me(request: Request):
        print("Getting Cookie:")
        user = request.cookies.get("session")
        if not user:
                print("No User")
                return {"logged-in": 0}
        else:
                print("Logged in as", user)
                conn = sqlite3.connect(ACC_DB)
                cur = conn.cursor()
                row = cur.execute("SELECT * FROM users WHERE username=?;", (user,)).fetchone()
                print(row)
                return {"logged-in": 1, "userID": row[0], "username": row[1], "favTeam": row[4], "coins": row[3]}

@router.post("/logout")
def logout():
        response = JSONResponse({"logged-in": 0})
        response.delete_cookie("session")
        return response

@router.post("/{userID}/beg")
def beg(userID):
        conn = sqlite3.connect(ACC_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        user = cur.execute("SELECT coins, last_beg FROM users WHERE userID=?;", (userID,)).fetchone()
        if not user:
                return JSONResponse({"status": 1, "error": "User not found"})
        lastBeg = user['last_beg']
        if lastBeg:
                last_beg_dt = datetime.fromisoformat(lastBeg)
                now = datetime.now()
                if last_beg_dt.date() == now.date():
                        conn.close()
                        return JSONResponse({"status": 1, "error": "You've already begged today!"})
        newCoins = user['coins'] + 10
        cur.execute("UPDATE users SET coins=?, last_beg=? WHERE userID=?;",
                    (newCoins, datetime.now().isoformat(), userID,)
        )
        conn.commit()
        conn.close()
        return JSONResponse({"status": 0})

class FavTeamUpdate(BaseModel):
        userID: int
        teamID: int

@router.post("/favTeam")
def changeFavTeam(update: FavTeamUpdate):
        print(update.userID)
        conn = sqlite3.connect(ACC_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("UPDATE users SET favTeam=? WHERE userID=?;", 
                    (update.teamID, update.userID))
        conn.commit()
        print(f"Updated User {update.userID}'s fave team to {update.teamID}")



# SELECT
#     t.teamID,
#     t.name,
#     SUM(CASE WHEN m.season = 1 AND (m.homeTeamID = t.teamID OR m.awayTeamID = t.teamID) AND m.matchPlayed = 1 THEN 1 ELSE 0 END) AS played,
#     SUM(CASE WHEN m.season = 1 AND m.winTeamID = t.teamID THEN 1 ELSE 0 END) AS wins,
#     SUM(CASE WHEN m.season = 1 AND m.winTeamID IS -1 AND (m.homeTeamID = t.teamID OR m.awayTeamID = t.teamID) THEN 1 ELSE 0 END) AS ties,
#     SUM(CASE WHEN m.season = 1 AND m.winTeamID IS NOT NULL AND m.winTeamID != t.teamID AND (m.homeTeamID = t.teamID OR m.awayTeamID = t.teamID) THEN 1 ELSE 0 END) AS losses,
#     (2 * SUM(CASE WHEN m.winTeamID = t.teamID THEN 1 ELSE 0 END)
#      + 1 * SUM(CASE WHEN m.winTeamID IS NULL 
#                     AND (m.homeTeamID = t.teamID OR m.awayTeamID = t.teamID) 
#                     THEN 1 ELSE 0 END)) AS points
# FROM teams t
# LEFT JOIN matches m
#     ON (t.teamID = m.homeTeamID OR t.teamID = m.awayTeamID)
# GROUP BY t.teamID, t.name;
# ORDER BY points DESC, wins DESC, 