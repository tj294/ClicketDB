import numpy.random as npr
import numpy as np
import json
import scipy.stats as stats
from typing import Dict, List
from fastapi import WebSocket

def generate_stat(low=0, high=1):
    return npr.uniform(low, high)

def up(x):
    return 1 + (x - 0.5)

def rand(statistic, scale=3, num=1):
    mu = statistic
    v = scale
    alpha = mu * v + 1
    beta = (1 - mu) * v + 1

    tn = stats.beta(alpha, beta)
    val = tn.rvs(num)
    # print(val)
    return val

def down(x):
    return 1 + (0.5 - x)

class Odds:
    def __init__(self, bat_stat, bowl_stat):
        # up = lambda x: 1 + (x-0.5)
        # down = lambda x: 1 + (0.5 - x)
        wideOdds = self.wideOdds(*bowl_stat)
        noBallOdds = self.noBallOdds(*bowl_stat)
        dotBallOdds = self.dotOdds(*bat_stat, *bowl_stat)
        wicketOdds = self.wicketOdds(*bat_stat, *bowl_stat)
        oneRunOdds = self.oneRunOdds(*bat_stat, *bowl_stat)
        twoRunsOdds = self.twoRunsOdds(*bat_stat, *bowl_stat)
        threeRunsOdds = self.threeRunsOdds(*bat_stat, *bowl_stat)
        fourRunsOdds = self.fourRunsOdds(*bat_stat, *bowl_stat)
        sixRunsOdds = self.sixRunsOdds(*bat_stat, *bowl_stat)
        normFactor = np.sum(
            [
                wideOdds,
                noBallOdds,
                dotBallOdds,
                wicketOdds,
                oneRunOdds,
                twoRunsOdds,
                threeRunsOdds,
                fourRunsOdds,
                sixRunsOdds,
            ]
        )

        self.wide = wideOdds / normFactor
        self.noBall = noBallOdds / normFactor
        self.dotBall = dotBallOdds / normFactor
        self.wicket = wicketOdds / normFactor
        self.oneRun = oneRunOdds / normFactor
        self.twoRuns = twoRunsOdds / normFactor
        self.threeRuns = threeRunsOdds / normFactor
        self.fourRuns = fourRunsOdds / normFactor
        self.sixRuns = sixRunsOdds / normFactor
        self.sum = 0
        # scale = lambda x: (x+0.5) - 1

    def wicketOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nWicket:")
        wickBase = 0.0494
        wickCoeff = (
            up(power)
            + down(technique)
            + up(aggression)
            + down(patience)
            + down(pace)
            + down(movement)
            + up(accuracy)
            + up(length)
        ) / 8
        # print(f"{wickCoeff} * {baseWick} = {wickCoeff*baseWick}")
        return wickCoeff * wickBase

    def dotOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nDot:")
        dotBase = 0.3507
        dotCo = (
            down(power)
            + up(technique)
            + down(aggression)
            + up(patience)
            + down(pace)
            + up(movement)
            + down(accuracy)
            + up(length)
        ) / 8
        # print(f"{dotCo} * {dotBase} = {dotCo*dotBase}")
        return dotCo * dotBase

    def wideOdds(self, pace, movement, accuracy, length):
        # print("\nWide:")
        wideBase = 0.0311
        wideCo = (up(pace) + up(movement) + down(accuracy) + down(length)) / 4
        # print(f"{wideCo} * {wideBase} + {wideCo*wideBase}")
        return wideCo * wideBase

    def noBallOdds(self, pace, movement, accuracy, length):
        # print("\nNo Ball:")
        noBallBase = 0.0040
        noBallCo = (up(pace) + down(movement) + down(accuracy) + up(length)) / 4
        # print(f"{noBallCo} * {noBallBase} + {noBallCo*noBallBase}")
        return noBallCo * noBallBase

    def oneRunOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nOne Run:")
        oneRunBase = 0.3714
        oneRunCo = (
            down(power)
            + up(technique)
            + down(aggression)
            + up(patience)
            + down(pace)
            + up(movement)
            + down(accuracy)
            + up(length)
        ) / 8
        # print(f"{oneRunCo} * {oneRunBase} + {oneRunCo*oneRunBase}")
        return oneRunCo * oneRunBase

    def twoRunsOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nTwo Runs:")
        twoRunBase = 0.0633
        twoRunCo = (down(power) + up(technique) + down(aggression) + up(patience)) / 4
        # print(f"{twoRunCo} * {twoRunBase} + {twoRunCo*twoRunBase}")
        return twoRunCo * twoRunBase

    def threeRunsOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nThree Runs:")
        threeRunBase = 0.0031
        threeRunCo = (up(power) + up(technique) + down(aggression) + down(patience)) / 4
        # print(f"{threeRunCo} * {threeRunBase} + {threeRunCo*threeRunBase}")
        return threeRunCo * threeRunBase

    def fourRunsOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nFour Runs:")
        fourRunBase = 0.1129
        fourRunCo = (
            up(power)
            + down(technique)
            + up(aggression)
            + down(patience)
            + up(pace)
            + down(movement)
            + up(accuracy)
            + down(length)
        ) / 8
        # print(f"{fourRunCo} * {fourRunBase} + {fourRunCo*fourRunBase}")
        return fourRunCo * fourRunBase

    def sixRunsOdds(
        self, power, technique, aggression, patience, pace, movement, accuracy, length
    ):
        # print("\nSix Runs:")
        sixRunBase = 0.0472
        sixRunCo = (
            up(power)
            + down(technique)
            + up(aggression)
            + down(patience)
            + up(pace)
            + down(movement)
            + up(accuracy)
            + down(length)
        ) / 8
        # print(f"{sixRunCo} * {sixRunBase} + {sixRunCo*sixRunBase}")
        return sixRunCo * sixRunBase

    def run_total(self, stat):
        self.sum += stat
        return self.sum

    def __str__(self):
        return f"Wicket: {self.wicket}, Dot: {self.dotBall}, Wide: {self.wide}, No Ball: {self.noBall}, 1 Run: {self.oneRun}, 2 Runs: {self.twoRuns}, 3 Runs: {self.threeRuns}, 4 Runs: {self.fourRuns}, 6 Runs: {self.sixRuns}"

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