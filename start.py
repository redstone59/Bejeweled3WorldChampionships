from bj3wc import *
from tkinter import filedialog

b = Bejeweled3WorldChampionships()
in_challenges = True
while in_challenges:
    challenge_file = filedialog.askopenfilename(title = "Open challenge file", filetypes = [("JSON file", ".json")])
    
    try:
        with open(challenge_file) as file:
            challenge = load_challenge_json(file.read())
            b.open_challenge(challenge)
        
        print(challenge)
        if not input("Play this challenge? (Y/N) ").lower().startswith("y"): continue
        
        b.start()
        in_challenges = input("Play another challenge? (Y/N) ").lower().startswith("y")
    except (InvalidChallengeError, InvalidSubchallengeError):
        print("Invalid challenge chosen!")