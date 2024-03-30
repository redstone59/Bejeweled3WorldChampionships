from bj3wc import *
from tkinter import filedialog, Tk

VER = "0.2-alpha"

def open_challenge_file():
    root = Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    file = filedialog.askopenfilename(parent = root, title = "Open challenge file", filetypes = [("JSON file", ".json")])
    root.destroy()
    return file

b = Bejeweled3WorldChampionships()
in_challenges = True

print(f"Bejeweled 3 World Championships v{VER}")
print("Find any bugs? Open an issue on the GitHub repo: https://github.com/redstone59/Bejeweled3WorldChampionships")

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
        
    except (InvalidChallengeError, InvalidSubchallengeError, FileNotFoundError) as e:
        print(f"{e.__class__}: {e}")
        print("Invalid challenge chosen!")