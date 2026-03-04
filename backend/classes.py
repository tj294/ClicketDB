from re import S
import numpy.random as npr
import numpy as np
import json
import scipy.stats as stats
from typing import Dict, List
from fastapi import WebSocket
from dataclasses import dataclass, asdict

def generate_stat(low=0, high=1):
    return npr.uniform(low, high)

# def up(x):
#     return 1 + (x - 0.5)

def rand(statistic, scale=3, num=1):
    mu = statistic
    v = scale
    alpha = mu * v + 1
    beta = (1 - mu) * v + 1

    tn = stats.beta(alpha, beta)
    val = tn.rvs(num)
    # print(val)
    return val

# def down(x):
#     return 1 + (0.5 - x)

import numpy as np
import random


def up(x):
    return 1 + (x - 0.5)

def down(x):
    return 1 + (0.5 - x)

# def rand(stat):
#     return max(0.0, min(1.0, stat + random.uniform(-0.1, 0.1)))


# ---------------------------------------------------------------------------
# Attribute definitions — add new ones here, no other code needs to change
# ---------------------------------------------------------------------------

ATTRIBUTES = {
    # Batting
    "PowerHitter":      {"fourRuns": 1.40, "sixRuns": 1.50, "dotBall": 0.80, "oneRun": 0.85, "wicket": 1.10},
    "Accumulator":      {"oneRun": 1.30, "twoRuns": 1.20, "dotBall": 1.10, "sixRuns": 0.60, "fourRuns": 0.80},
    "AggressiveOpener": {"fourRuns": 1.20, "sixRuns": 1.25, "wicket": 1.15, "dotBall": 0.90},
    "NervousStarter":   {"dotBall": 1.15, "oneRun": 1.10, "wicket": 1.10, "sixRuns": 0.70},
    "Finisher":         {"sixRuns": 1.35, "fourRuns": 1.20, "wicket": 1.05, "dotBall": 0.85},
    # Bowling
    "PaceMerchant":     {"wide": 1.20, "wicket": 1.15, "fourRuns": 1.10, "dotBall": 1.10},
    "LegSpinner":       {"wicket": 1.30, "dotBall": 1.20, "wide": 1.15, "oneRun": 0.85, "fourRuns": 0.90},
    "OffSpinner":       {"dotBall": 1.20, "wicket": 1.15, "twoRuns": 0.90, "fourRuns": 0.85},
    "SwingBowler":      {"wicket": 1.25, "dotBall": 1.15, "wide": 1.10, "fourRuns": 0.90},
    "AccurateBowler":   {"dotBall": 1.30, "wide": 0.50, "noBall": 0.50, "wicket": 1.10},
    "WildCard":         {"wide": 1.40, "noBall": 1.30, "sixRuns": 1.20, "wicket": 1.20, "dotBall": 0.80},
}


# ---------------------------------------------------------------------------
# BatterState
# ---------------------------------------------------------------------------

class BatterState:
    """
    Create one instance when a batter walks in.
    Pass to get_outcome() each ball. Call record_ball() after each legal delivery.
    Create a fresh instance when a wicket falls.
    """

    def __init__(self):
        self.balls_faced = 0
        self.consecutive_dots = 0
        self.runs_scored = 0

    def confidence_modifiers(self) -> dict:
        """Builds over ~30 balls. Batters start cautious, grow into big shots."""
        conf = min(self.balls_faced / 30.0, 1.0)
        return {
            "sixRuns":  1.0 + 0.40 * conf,
            "fourRuns": 1.0 + 0.25 * conf,
            "twoRuns":  1.0 + 0.15 * conf,
            "dotBall":  1.0 - 0.20 * conf,
            "wicket":   1.0 - 0.10 * conf,
            "oneRun":   1.0 + 0.10 * (1 - conf),
        }

    def dot_pressure_modifiers(self) -> dict:
        """After 3+ consecutive dots, batter panics and takes more risks."""
        dots = max(0, self.consecutive_dots - 2)
        pressure = min(dots / 5.0, 1.0)
        return {
            "sixRuns":  1.0 + 0.35 * pressure,
            "fourRuns": 1.0 + 0.25 * pressure,
            "wicket":   1.0 + 0.20 * pressure,
            "dotBall":  1.0 - 0.15 * pressure,
        }

    def record_ball(self, runs: int):
        """Call after every legal delivery (not wides/no-balls)."""
        self.balls_faced += 1
        self.runs_scored += runs
        if runs == 0:
            self.consecutive_dots += 1
        else:
            self.consecutive_dots = 0


# ---------------------------------------------------------------------------
# MatchContext
# ---------------------------------------------------------------------------

class MatchContext:
    """
    Situational modifiers. Update current_score and balls_remaining each ball.

    innings         : 1 or 2
    balls_remaining : legal balls left (starts 120)
    wickets_in_hand : wickets remaining (starts 10)
    target          : runs needed to win (first_innings_runs + 1). None in 1st innings.
    current_score   : runs scored so far this innings
    """

    def __init__(self, innings=1, balls_remaining=120,
                 wickets_in_hand=10, target=None, current_score=0):
        self.innings = innings
        self.balls_remaining = max(1, balls_remaining)
        self.wickets_in_hand = wickets_in_hand
        self.target = target
        self.current_score = current_score

    @property
    def required_runs(self):
        return None if self.target is None else max(0, self.target - self.current_score)

    @property
    def current_rr(self) -> float:
        balls_bowled = 120 - self.balls_remaining
        return 0.0 if balls_bowled <= 0 else self.current_score / balls_bowled

    @property
    def required_rr(self):
        return None if self.required_runs is None else self.required_runs / self.balls_remaining

    def situational_modifiers(self) -> dict:
        mods = {k: 1.0 for k in
                ["wicket", "dotBall", "oneRun", "twoRuns", "threeRuns",
                 "fourRuns", "sixRuns", "wide", "noBall"]}

        # Death overs aggression (last 30 balls)
        death = max(0.0, 1.0 - self.balls_remaining / 30.0)
        mods["sixRuns"]  *= 1.0 + 0.50 * death
        mods["fourRuns"] *= 1.0 + 0.35 * death
        mods["wicket"]   *= 1.0 + 0.25 * death
        mods["dotBall"]  *= 1.0 - 0.20 * death

        # Wickets in hand (-0.5 to +0.5 factor)
        wf = (self.wickets_in_hand - 5) / 10.0
        mods["sixRuns"]  *= 1.0 + 0.30 * wf
        mods["fourRuns"] *= 1.0 + 0.20 * wf
        mods["wicket"]   *= 1.0 - 0.15 * wf
        mods["dotBall"]  *= 1.0 - 0.10 * wf

        # 2nd innings RRR
        if self.innings == 2 and self.required_rr is not None:
            gap = self.required_rr - self.current_rr
            if gap > 0:
                panic = min(gap / 0.5, 1.0)
                mods["sixRuns"]  *= 1.0 + 0.60 * panic
                mods["fourRuns"] *= 1.0 + 0.40 * panic
                mods["wicket"]   *= 1.0 + 0.30 * panic
                mods["dotBall"]  *= 1.0 - 0.25 * panic
                mods["oneRun"]   *= 1.0 - 0.10 * panic
            else:
                comfort = min(-gap / 0.3, 1.0)
                mods["oneRun"]   *= 1.0 + 0.20 * comfort
                mods["twoRuns"]  *= 1.0 + 0.15 * comfort
                mods["sixRuns"]  *= 1.0 - 0.30 * comfort
                mods["fourRuns"] *= 1.0 - 0.20 * comfort
                mods["wicket"]   *= 1.0 - 0.20 * comfort

        return mods


# ---------------------------------------------------------------------------
# Odds
# ---------------------------------------------------------------------------

class Odds:
    OUTCOME_KEYS = ["wide", "noBall", "dotBall", "wicket",
                    "oneRun", "twoRuns", "threeRuns", "fourRuns", "sixRuns"]

    def __init__(self, bat_stat, bowl_stat,
                 batter_attributes=None, bowler_attributes=None,
                 batter_state=None, match_context=None):
        batter_attributes = batter_attributes or []
        bowler_attributes = bowler_attributes or []

        raw = {
            "wide":      self.wideOdds(*bowl_stat),
            "noBall":    self.noBallOdds(*bowl_stat),
            "dotBall":   self.dotOdds(*bat_stat, *bowl_stat),
            "wicket":    self.wicketOdds(*bat_stat, *bowl_stat),
            "oneRun":    self.oneRunOdds(*bat_stat, *bowl_stat),
            "twoRuns":   self.twoRunsOdds(*bat_stat, *bowl_stat),
            "threeRuns": self.threeRunsOdds(*bat_stat, *bowl_stat),
            "fourRuns":  self.fourRunsOdds(*bat_stat, *bowl_stat),
            "sixRuns":   self.sixRunsOdds(*bat_stat, *bowl_stat),
        }

        for attr in batter_attributes + bowler_attributes:
            if attr in ATTRIBUTES:
                for outcome, mult in ATTRIBUTES[attr].items():
                    if outcome in raw:
                        raw[outcome] *= mult

        if batter_state is not None:
            for mod_dict in [batter_state.confidence_modifiers(),
                             batter_state.dot_pressure_modifiers()]:
                for outcome, mult in mod_dict.items():
                    if outcome in raw:
                        raw[outcome] *= mult

        if match_context is not None:
            for outcome, mult in match_context.situational_modifiers().items():
                if outcome in raw:
                    raw[outcome] *= mult

        total = sum(raw.values())
        for key in self.OUTCOME_KEYS:
            setattr(self, key, raw[key] / total)

        self.sum = 0.0

    def wicketOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((up(power) + down(technique) + up(aggression) + down(patience)
                 + down(pace) + down(movement) + up(accuracy) + up(length)) / 8) * 0.0494

    def dotOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((down(power) + up(technique) + down(aggression) + up(patience)
                 + down(pace) + up(movement) + down(accuracy) + up(length)) / 8) * 0.3507

    def wideOdds(self, pace, movement, accuracy, length):
        return ((up(pace) + up(movement) + down(accuracy) + down(length)) / 4) * 0.0311

    def noBallOdds(self, pace, movement, accuracy, length):
        return ((up(pace) + down(movement) + down(accuracy) + up(length)) / 4) * 0.0040

    def oneRunOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((down(power) + up(technique) + down(aggression) + up(patience)
                 + down(pace) + up(movement) + down(accuracy) + up(length)) / 8) * 0.3714

    def twoRunsOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((down(power) + up(technique) + down(aggression) + up(patience)) / 4) * 0.0633

    def threeRunsOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((up(power) + up(technique) + down(aggression) + down(patience)) / 4) * 0.0031

    def fourRunsOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((up(power) + down(technique) + up(aggression) + down(patience)
                 + up(pace) + down(movement) + up(accuracy) + down(length)) / 8) * 0.1129

    def sixRunsOdds(self, power, technique, aggression, patience, pace, movement, accuracy, length):
        return ((up(power) + down(technique) + up(aggression) + down(patience)
                 + up(pace) + down(movement) + up(accuracy) + down(length)) / 8) * 0.0472

    def run_total(self, stat):
        self.sum += stat
        return self.sum

    def __str__(self):
        return (f"Wicket: {self.wicket:.4f}, Dot: {self.dotBall:.4f}, "
                f"Wide: {self.wide:.4f}, No Ball: {self.noBall:.4f}, "
                f"1R: {self.oneRun:.4f}, 2R: {self.twoRuns:.4f}, "
                f"3R: {self.threeRuns:.4f}, 4R: {self.fourRuns:.4f}, 6R: {self.sixRuns:.4f}")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, gameID: int, websocket: WebSocket):
        await websocket.accept()
        if gameID not in self.active_connections:
            self.active_connections[gameID] = []
        self.active_connections[gameID].append(websocket)
    
    def disconnect(self, gameID: int, websocket: WebSocket):
        self.active_connections[gameID].remove(websocket)
        if not self.active_connections[gameID]:
            del self.active_connections[gameID]
    
    async def broadcast(self, gameID: int, message: dict):
        if gameID in self.active_connections:
            dead_sockets = []
            for ws in self.active_connections[gameID]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    dead_sockets.append(ws)
            
            for ws in dead_sockets:
                self.disconnect(gameID, ws)


class OddsLogger:
    """
    Lightweight per-ball logger. Writes JSON-lines so the file stays readable
    even if the simulation crashes mid-innings.
    """

    OUTCOME_KEYS = ["wide", "noBall", "dotBall", "wicket",
                    "oneRun", "twoRuns", "threeRuns", "fourRuns", "sixRuns"]

    def __init__(self, filepath: str):
        self.filepath = filepath
        # Truncate / create fresh file at the start of each innings
        open(filepath, "w").close()

    def log(
        self,
        over: int,
        ball_in_over: int,
        batter: dict,
        bowler: dict,
        # bat_stat: list,
        # bowl_stat: tuple,
        odds_before: "Odds",   # Odds built with NO modifiers
        odds_after: "Odds",    # Odds built with ALL modifiers
        batter_state: "BatterState",
        match_context: "MatchContext",
        outcome: str,          # the result symbol  e.g. "W", "4", "·"
        runs: int,
    ):
        record = {
            "over": over,
            "ball": ball_in_over,
            "batter": f"{batter['fname']} {batter['lname']}",
            "bowler": f"{bowler['fname']} {bowler['lname']}",
            # # Raw per-ball stats used
            # "bat_stat": {
            #     "power":      bat_stat[0],
            #     "technique":  bat_stat[1],
            #     "aggression": bat_stat[2],
            #     "patience":   bat_stat[3],
            # },
            # "bowl_stat": {
            #     "pace":      bowl_stat[0],
            #     "movement":  bowl_stat[1],
            #     "accuracy":  bowl_stat[2],
            #     "length":    bowl_stat[3],
            # },
            # Base odds (stats only, no modifiers)
            "odds_base": {k: np.round(getattr(odds_before, k), 5).tolist()
                          for k in self.OUTCOME_KEYS},
            # Final odds (all modifiers applied)
            "odds_final": {k: np.round(getattr(odds_after, k), 5).tolist()
                           for k in self.OUTCOME_KEYS},
            # Batter state at the moment of delivery
            "batter_state": {
                "balls_faced":       batter_state.balls_faced,
                "consecutive_dots":  batter_state.consecutive_dots,
                "runs_scored":       batter_state.runs_scored,
            },
            # Match context at the moment of delivery
            "match_context": {
                "innings":          match_context.innings,
                "balls_remaining":  match_context.balls_remaining,
                "wickets_in_hand":  match_context.wickets_in_hand,
                "current_score":    match_context.current_score,
                "target":           match_context.target,
                "current_rr":       round(match_context.current_rr, 4),
                "required_rr":      round(match_context.required_rr, 4)
                                    if match_context.required_rr is not None else None,
            },
            "outcome": outcome,
            "runs": runs,
        }
        with open(self.filepath, "a") as f:
            f.write(json.dumps(record) + "\n")