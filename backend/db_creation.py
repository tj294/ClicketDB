import sqlite3
import os
from generation import (
    generate_players_per_team,
    regenerate_fixtures,
    visualize_schedule_distribution,
)
import csv
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DBNAME")

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

# Define local rivals
local_rivals = {
    "Birmingham Bullfrogs": "Nottingham Nightingales",
    "Brighton Beachcombers": "Parliamentary Penpushers",
    "Bristol Bats": "Cardiff Cwtchers",
    "Cornwall Catastrophes": "Devon Devils",
    "Edinburgh XI": "Glasgow Goofballs",
    "Manchester Monsters": "Yorkshire Puddings",
}

# Flatten to a unique list of teams
all_teams = list(set(local_rivals.keys()) | set(local_rivals.values()))

# Connect to the database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Recreate teams table
cursor.execute(
    """
CREATE TABLE teams (
    teamID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    localRival INTEGER,
    gamesPlayed INTEGER DEFAULT 0,
    gamesWon INTEGER DEFAULT 0,
    gamesLost INTEGER DEFAULT 0,
    gamesTied INTEGER DEFAULT 0,
    oversFaced REAL DEFAULT 0,
    runsScored INTEGER DEFAULT 0,
    oversBowled REAL DEFAULT 0,
    runsConceded INTEGER DEFAULT 0,
    FOREIGN KEY (localRival) REFERENCES teams(teamID)
)
"""
)

# Insert teams
team_ids = {}
for team in all_teams:
    cursor.execute("INSERT INTO teams (name) VALUES (?)", (team,))
    team_ids[team] = cursor.lastrowid

# Set local rivals
for team, rival in local_rivals.items():
    cursor.execute(
        "UPDATE teams SET localRival = ? WHERE name = ?", (team_ids[rival], team)
    )
    cursor.execute(
        "UPDATE teams SET localRival = ? WHERE name = ?", (team_ids[team], rival)
    )

conn.commit()

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS live (
#         matchID INTEGER PRIMARY KEY AUTOINCREMENT,
#         season INTEGER,
#         match INTEGER,
#         homeTeamID INTEGER,
#         awayTeamID INTEGER,
#         batFirstID INTEGER,
#         bFRuns INTEGER,
#         bFWickets INTEGER,
#         bFOvers TEXT,
#         bSRuns INTEGER,
#         bSWickets INTEGER,
#         bSOvers TEXT,
#         batter1ID INTEGER,
#         batter1FName TEXT,
#         batter1LName TEXT,
#         batter1Runs INTEGER,
#         batter1Balls INTEGER,
#         batter1Fours INTEGER,
#         batter1Sixes INTEGER,
#         batter1SR REAL,
#         batter2ID INTEGER,
#         batter2FName TEXT,
#         batter2LName TEXT,
#         batter2Runs INTEGER,
#         batter2Balls INTEGER,
#         batter2Fours INTEGER,
#         batter2Sixes INTEGER,
#         batter2SR REAL,
#         sBatID INTEGER,
#         bowler1ID INTEGER,
#         bowler1FName TEXT,
#         bowler1LName TEXT,
#         bowler1Overs TEXT,
#         bowler1Maidens INTEGER,
#         bowler1Runs INTEGER,
#         bowler1Wickets INTEGER,
#         bowler1Econ REAL,
#         bowler2ID INTEGER,
#         bowler2FName TEXT,
#         bowler2LName TEXT,
#         bowler2Overs TEXT,
#         bowler2Maidens INTEGER,
#         bowler2Runs INTEGER,
#         bowler2Wickets INTEGER,
#         bowler2Econ REAL,
#         currentBowlerID INTEGER,
#         currentOver INTEGER,
#         currentBall INTEGER,
#         overResults TEXT,
#         ballEvent TEXT,
#         ballText TEXT,
#         lastBat TEXT,
#         fbattingCard TEXT,
#         fyetToBat TEXT,
#         sbattingCard TEXT,
#         syetToBat TEXT
#     )
# """)
print("Database reset and seeded successfully.")

print("Generating Players...")
# --- Players table ---
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS players (
    playerID INTEGER PRIMARY KEY AUTOINCREMENT,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    power INTEGER,
    technique INTEGER,
    aggression INTEGER,
    patience INTEGER,
    pace INTEGER,
    movement INTEGER,
    accuracy INTEGER,
    length INTEGER
)
"""
)

# --- Player career stats ---
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS player_career_stats (
    playerID INTEGER PRIMARY KEY,
    matches_played INTEGER DEFAULT 0,
    innings_batted INTEGER DEFAULT 0,
    runs_scored INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    highest_score TEXT DEFAULT '0',
    highest_balls_faced INTEGER DEFAULT 0,
    best_bat_ID INTEGER,
    not_outs INTEGER DEFAULT 0,
    fifties INTEGER DEFAULT 0,
    hundreds INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    innings_bowled INTEGER DEFAULT 0,
    overs_bowled TEXT DEFAULT '0.0',
    maidens_bowled INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    wickets_taken INTEGER DEFAULT 0,
    best_figures_wickets INTEGER DEFAULT 0,
    best_figures_runs INTEGER DEFAULT 0,
    best_bowl_ID INTEGER,
    FOREIGN KEY (playerID) REFERENCES players(playerID)
)
"""
)

# --- Player-team relationship table (for transfers) ---
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS player_teams (
    playerID INTEGER,
    teamID INTEGER,
    start_date TEXT,
    end_date TEXT,
    PRIMARY KEY (playerID, start_date),
    FOREIGN KEY (playerID) REFERENCES players(playerID),
    FOREIGN KEY (teamID) REFERENCES teams(teamID)
)
"""
)
conn.commit()

generate_players_per_team(11)

print("Generating Fixtures...")
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS matches (
    matchID INTEGER PRIMARY KEY AUTOINCREMENT,
    season INTEGER,
    matchNo INTEGER,
    round INTEGER,
    homeTeamID INTEGER,
    awayTeamID INTEGER,
    scheduledDate TEXT,
    matchPlayed INTEGER DEFAULT 0,
    result TEXT DEFAULT TBC,
    homeScore TEXT DEFAULT YTB,
    awayScore TEXT DEFAULT YTB,
    log TEXT DEFAULT NULL,
    batFirstID INTEGER,
    bFRuns INTEGER,
    bFWickets INTEGER,
    bFOvers TEXT,
    bSRuns INTEGER DEFAULT 0,
    bSWickets INTEGER DEFAULT 0,
    bSOvers TEXT DEFAULT YTB,
    batter1ID INTEGER,
    batter1FName TEXT,
    batter1LName TEXT,
    batter1Runs INTEGER,
    batter1Balls INTEGER,
    batter1Fours INTEGER,
    batter1Sixes INTEGER,
    batter1SR REAL,
    batter2ID INTEGER,
    batter2FName TEXT,
    batter2LName TEXT,
    batter2Runs INTEGER,
    batter2Balls INTEGER,
    batter2Fours INTEGER,
    batter2Sixes INTEGER,
    batter2SR REAL,
    sBatID INTEGER,
    bowler1ID INTEGER,
    bowler1FName TEXT,
    bowler1LName TEXT,
    bowler1Overs TEXT,
    bowler1Maidens INTEGER,
    bowler1Runs INTEGER,
    bowler1Wickets INTEGER,
    bowler1Econ REAL,
    bowler2ID INTEGER,
    bowler2FName TEXT,
    bowler2LName TEXT,
    bowler2Overs TEXT,
    bowler2Maidens INTEGER,
    bowler2Runs INTEGER,
    bowler2Wickets INTEGER,
    bowler2Econ REAL,
    currentBowlerID INTEGER,
    currentOver INTEGER,
    currentBall INTEGER,
    overResults TEXT,
    ballEvent TEXT,
    ballText TEXT,
    lastBat TEXT,
    fbattingCard TEXT,
    fyetToBat TEXT,
    fbowlingCard TEXT,
    sbattingCard TEXT,
    syetToBat TEXT,
    sbowlingCard TEXT,
    FOREIGN KEY (homeTeamID) REFERENCES teams(teamID),
    FOREIGN KEY (awayTeamID) REFERENCES teams(teamID)
)
"""
)

conn.commit()

regenerate_fixtures()

cursor.execute(
    """
        SELECT m.matchID, t1.name, t2.name, m.scheduledDate
        FROM matches m
        JOIN teams t1 ON m.homeTeamID = t1.teamID
        JOIN teams t2 ON m.awayTeamID = t2.teamID
        ORDER BY m.scheduledDate
    """
)

fixtures = cursor.fetchall()
filename = "fixtures.csv"
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["MatchID", "Home Team", "Away Team", "Date"])
    writer.writerows(fixtures)

print(f"Fixtures exported to {filename}")

visualize_schedule_distribution()

conn.close()
