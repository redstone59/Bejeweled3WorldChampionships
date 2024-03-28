from bj3wc import *
from tkinter import filedialog, Tk

def open_challenge_file():
    root = Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    file = filedialog.askopenfilename(parent = root, title = "Open challenge file", filetypes = [("JSON file", ".json")])
    root.destroy()
    return file

b = Bejeweled3WorldChampionships()
in_challenges = True
while in_challenges:
    challenge_file = open_challenge_file()
    
    try:
        with open(challenge_file) as file:
            challenge = load_challenge_json(file.read())
            b.open_challenge(challenge)
        
        print(challenge)
        if not input("Play this challenge? (Y/N) ").lower().startswith("y"): continue
        
        b.start()
        in_challenges = input("Play another challenge? (Y/N) ").lower().startswith("y")
    except (InvalidChallengeError, InvalidSubchallengeError, FileNotFoundError):
        print("Invalid challenge chosen!")