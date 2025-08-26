import sqlite3
from numpy.random import uniform
import random
from datetime import date, timedelta, datetime
from itertools import combinations
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_NAME = getenv("DBNAME")


def load_names(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]


def generate_players_per_team(n_players_per_team=11, start_date="Season 0"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Load name lists
    first_names = load_names("first_names.txt")
    last_names = load_names("last_names.txt")

    # Get all teamIDs
    cursor.execute("SELECT teamID FROM teams")
    team_ids = [row[0] for row in cursor.fetchall()]

    for team_id in team_ids:
        for _ in range(n_players_per_team):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"

            # Random skill stats (1–100)
            power = random.uniform(0, 1.0)
            tech = random.uniform(0, 1.0)
            aggr = random.uniform(0, 1.0)
            pat = random.uniform(0, 1.0)
            pace = random.uniform(0, 1.0)
            move = random.uniform(0, 1.0)
            acc = random.uniform(0, 1.0)
            length = random.uniform(0, 1.0)

            # Insert into players table
            cursor.execute(
                """
                INSERT INTO players (
                    fname, lname, power, technique, aggression, patience,
                    pace, movement, accuracy, length
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    fname,
                    lname,
                    power,
                    tech,
                    aggr,
                    pat,
                    pace,
                    move,
                    acc,
                    length,
                ),
            )

            player_id = cursor.lastrowid

            # Create empty stats row
            cursor.execute(
                """
                INSERT INTO player_career_stats (playerID)
                VALUES (?)
            """,
                (player_id,),
            )

            # Assign to team
            cursor.execute(
                """
                INSERT INTO player_teams (playerID, teamID, start_date)
                VALUES (?, ?, ?)
            """,
                (player_id, team_id, start_date),
            )

    conn.commit()
    conn.close()
    print(
        f"{n_players_per_team * len(team_ids)} players generated and assigned to teams."
    )


# Dictionary of team name to local rival name
local_rivals = {
    "Birmingham Bullfrogs": "Nottingham Nightingales",
    "Brighton Beachcombers": "Parliamentary Penpushers",
    "Bristol Bats": "Cardiff Cwtchers",
    "Cornwall Catastrophes": "Devon Devils",
    "Edinburgh XI": "Glasgow Goofballs",
    "Manchester Monsters": "Yorkshire Puddings",
}


def generate_time_slots():
    base = datetime.strptime("2025-08-10 00:00", "%Y-%m-%d %H:%M")  # Monday
    return [base + timedelta(hours=i) for i in range(6 * 24)]  # 144 hourly slots


def rotate(teams):
    top_line = teams[0]
    bottom_line = teams[1]
    fixed_game = top_line.pop(0)
    game_to_move = bottom_line.pop(0)
    top_line.insert(0, game_to_move)
    top_line.insert(0, fixed_game)
    game_to_move = top_line.pop(-1)
    bottom_line.append(game_to_move)
    teams = [top_line, bottom_line]
    return teams


def regenerate_fixtures():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Start New Season
    lastSeason = cursor.execute("SELECT MAX(season) FROM matches").fetchone()[0]

    if lastSeason == None:
        seasonID = 1
    else:
        seasonID = lastSeason + 1

    # Clear old matches
    # print(cursor.execute("DELETE FROM matches"))
    # conn.commit()

    # Get teams from DB (teamID, name)
    cursor.execute("SELECT teamID, name FROM teams")
    teams = cursor.fetchall()
    id_to_name = {tid: name for tid, name in teams}
    name_to_id = {name: tid for tid, name in teams}

    team_names = [name for _, name in teams]
    random.shuffle(team_names)

    # Split into two groups of 6 for rotation
    top_line = team_names[:6]
    bottom_line = team_names[6:]
    teams_rot = [top_line, bottom_line]

    rounds = {}
    N_rounds = 11
    N_matches = 6

    # Create rounds 1 to 11 using rotation
    for round_no in range(1, N_rounds + 1):
        matches = []
        for i in range(N_matches):
            home = teams_rot[0][i]
            away = teams_rot[1][i]
            matches.append((name_to_id[home], name_to_id[away]))
        rounds[f"Round {round_no}"] = matches
        teams_rot = rotate(teams_rot)

    # Add local derby round 12
    local_matches = []
    for home_team_name, away_team_name in local_rivals.items():
        home_id = name_to_id[home_team_name]
        away_id = name_to_id[away_team_name]
        local_matches.append((home_id, away_id))
    rounds["Round 12"] = local_matches

    # Schedule rounds: 2 rounds per day, 9am to 9pm (hourly games)
    base_date = datetime.strptime("2025-08-18 09:00", "%Y-%m-%d %H:%M")  # Monday 9am
    match_entries = []
    matchNo = 0
    for day in range(6):  # Monday to Saturday
        for round_idx in range(2):  # 2 rounds per day
            round_number = day * 2 + round_idx + 1
            round_key = f"Round {round_number}"
            start_time = base_date + timedelta(
                days=day, hours=round_idx * 6
            )  # 9am or 3pm
            matches = rounds[round_key]
            for i, (home_id, away_id) in enumerate(matches):
                matchNo += 1
                match_time = start_time + timedelta(hours=i)
                scheduledDate = match_time.strftime("%Y-%m-%d %H:%M")
                match_entries.append((seasonID, matchNo, home_id, away_id, scheduledDate, round_number))

    # Insert into DB
    cursor.executemany(
        """
        INSERT INTO matches (season, matchNo, homeTeamID, awayTeamID, scheduledDate, round)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        match_entries,
    )

    conn.commit()
    conn.close()
    print("✅ Fixtures generated and saved to database.")


def visualize_schedule_distribution():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get team ID → name mapping
    cursor.execute("SELECT teamID, name FROM teams")
    teams = dict(cursor.fetchall())

    # Initialize: team_name → [0, 0, 0, 0, 0, 0] for Mon–Sat
    team_schedule = {name: [0] * 6 for name in teams.values()}

    # Get all scheduled matches
    cursor.execute("SELECT homeTeamID, awayTeamID, scheduledDate FROM matches")
    matches = cursor.fetchall()

    for homeID, awayID, date_str in matches:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        day = date.weekday()  # 0 = Mon, 5 = Sat
        if day > 5:
            continue  # skip Sundays (shouldn't happen)

        home = teams[homeID]
        away = teams[awayID]
        team_schedule[home][day] += 1
        team_schedule[away][day] += 1

    # Display header
    print("\n🗓️ Schedule Distribution Table (matches per day)")
    print("Team".ljust(30), "Mon  Tue  Wed  Thu  Fri  Sat")
    print("-" * 60)

    # Display table
    for team, counts in sorted(team_schedule.items()):
        row = "  ".join(str(c).rjust(3) for c in counts)
        print(team.ljust(30), row)

    conn.close()

if __name__ == '__main__':
    regenerate_fixtures()