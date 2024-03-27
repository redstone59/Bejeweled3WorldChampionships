from bj3wc import *

b = Bejeweled3WorldChampionships()
with open("./challenges/Challenge A (Easy).json") as file:
    b.open_challenge(load_challenge_json(file.read()))
b.start()