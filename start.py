from bj3wc import *

GAME_STRING = """
{
  "challenge_information": {
    "name": "Challenge D",
    "author": "redstone59",
    "description": "Very difficult challenge included with BJ3WC.",
    "mode": "timed",
    "time": 600
  },
  "subchallenges": [
    {
        "objective": "LightMult",
        "mode": "value",
        "condition": 8,
        "multiplier": 1
    },
    {
        "objective": "PokerHand",
        "mode": "value",
        "condition": 10,
        "timebonus": 1,
        "time": "60",
        "extra": "Full House",
        "multiplier": 1
    },
    {
        "objective": "Balance",
        "mode": "timed",
        "time": 60,
        "multiplier": 10
    },
    {
        "objective": "IceStorm",
        "mode": "value",
        "condition": 500000,
        "timebonus": 1,
        "time": "120",
        "multiplier": 1
    },
    {
        "objective": "MatchBomb",
        "mode": "value",
        "condition": 10,
        "extra": 8,
        "multiplier": 1
    },
    {
        "objective": "Poker",
        "mode": "endless",
        "multiplier": 25
    }
  ]  
}
"""

b = Bejeweled3WorldChampionships()
b.open_challenge(load_challenge_json(GAME_STRING))
b.start()