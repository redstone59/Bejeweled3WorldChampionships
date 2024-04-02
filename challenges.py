from dataclasses import *
from typing import Literal

import json
import os, sys, pathlib

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CHALLENGE_DATA: dict = json.load(open(pathlib.Path(PATH, "challenges.json")))

class InvalidChallengeError(Exception):
    pass

class InvalidSubchallengeError(Exception):
    pass

@dataclass
class Subchallenge:
    objective: str
    mode: Literal["value", "timed", "endless"]
    multiplier: int
    condition: int | None = None
    time_bonus_enabled: bool = False
    time: int | None = None
    """
    `extra` does the following for these modes:
    
    Avalanche: Number of gems dropped after a move. (Typically 5)
    Butterflies: Number of moves before butterflies move upwards. (Typically 1)
    Match Bomb/Time Bomb: Starting number on newly spawned bombs. (Typically 30)
    """
    extra: int | str | None = None
    
    def to_dict(self):
        result = {}
        result["objective"] = self.objective
        result["mode"] = self.mode
        
        if self.mode == "value": result["condition"] = self.condition
        if self.time_bonus_enabled: result["time_bonus"] = True
        if self.time != None: result["time"] = self.time
        if self.extra != None: result["extra"] = self.extra
        
        result["multiplier"] = self.multiplier

        return result
    
    def get_initial_value(self):
        open_requirements = CHALLENGE_DATA[self.objective]["requirements"]
        
        if "initial_value" in open_requirements:
            initial_value = open_requirements["initial_value"]
        else:
            initial_value = 0
        
        return initial_value
    
    def get_gui_string(self):
        subchallenge_strings: dict = CHALLENGE_DATA[self.objective]["strings"]["abbreviated"]
        
        if self.mode == "value":
            result_string: str = subchallenge_strings["value"]
            result_string = result_string.replace("<condition>", str(self.condition))
            if self.time_bonus_enabled:
                result_string += f" ({self.time}s)"
        elif self.mode == "endless":
            result_string: str = subchallenge_strings["timed"]
            result_string += " (endless)"
        else:
            result_string: str = subchallenge_strings["timed"]
            result_string += f" ({self.time}s)"
        
        if self.objective == "PokerHand":
            result_string = result_string.replace("<extra>", str(self.extra) + "s")
        elif self.extra != None:
            result_string += f" [{self.extra}]"
        
        return result_string
    
    def __str__(self):
        subchallenge_strings: dict = CHALLENGE_DATA[self.objective]["strings"]
        if "suffix" in subchallenge_strings.keys(): suffix = subchallenge_strings["suffix"]
        subchallenge_strings = subchallenge_strings["expanded"]
        
        if self.mode == "value":
            result_string: str = subchallenge_strings["value"]
            result_string = result_string.replace("<condition>", str(self.condition))
            if self.time_bonus_enabled:
                result_string = result_string[:-1] # This smells bad.
                result_string += " as quickly as possible!"
        elif self.mode == "endless":
            result_string: str = subchallenge_strings["timed"]
            result_string = result_string.replace("<suffix>", "until the challenge ends")
        else:
            result_string: str = subchallenge_strings["timed"]
            result_string = result_string.replace("<suffix>", suffix)
            result_string = result_string.replace("<time>", str(self.time))
        
        if self.objective == "PokerHand" and self.condition >= 2:
            result_string = result_string.replace("<extra>", str(self.extra) + "s")
        else:
            result_string = result_string.replace("<extra>", str(self.extra))
        
        return result_string

@dataclass
class Challenge:
    name: str
    author: str
    description: str
    mode: Literal["timed", "marathon"]
    subchallenges: list[Subchallenge]
    time: int | None = None
    
    def is_over(self):
        return len(self.subchallenges) == 0
    
    def next(self):
        if self.is_over(): return None
        return self.subchallenges.pop(0)
    
    def to_dict(self):
        challenge_dict = {}
        challenge_dict["challenge_information"] = {"name": self.name,
                                                   "author": self.author,
                                                   "description": self.description,
                                                   "mode": self.mode,
                                                   }
        if self.mode == "timed": challenge_dict["challenge_information"]["time"] = self.time
        
        challenge_dict["subchallenges"] = [subchallenge.to_dict() for subchallenge in self.subchallenges]
        
        return challenge_dict
    
    def __str__(self):
        return f"""
{self.name} by {self.author}
{len(self.subchallenges)} challenges long.
{"Marathon challenge" if self.mode == "marathon" else f"Timed challenge: Lasts {self.time // 60}m {self.time % 60}s"}

{self.description}
"""

def check_challenge_metadata(metadata: dict):
    """
    Raises an error if a challenge's metadata is incorrect.
    
    Raises `InvalidChallengeError` if:
    - The challenge's metadata is missing a required field (name, author, description, mode).
    - The challenge's mode is not "timed" or "marathon".
    - A timed challenge does not specify a time.
    """
    
    for required in ["name", "author", "description", "mode"]:
        if required not in metadata.keys():
            raise InvalidChallengeError(f"Invalid challenge JSON, metadata missing required field '{required}'.")
    
    if metadata["mode"] not in ["timed", "marathon"]:
        raise InvalidChallengeError(f"Invalid mode {metadata["mode"]} in challenge. Valid options are 'timed' or 'marathon'.")
    
    if metadata["mode"] == "timed" and "time" not in metadata.keys():
        raise InvalidChallengeError("No time specified for timed challenge.")

def check_subchallenge_data(subchallenge: dict):
    """
    Raises an error if a subchallenge's data is incorrect.
    
    Raises `InvalidSubchallengeError` if:
    - The subchallenge is missing a required field (objective, mode, multiplier)
    - The subchallenge's mode is not "value", "timed", or "endless".
    - The subchallenge has an invalid mode for the objective.
    - There is no `condition` field for any `value` subchallenge.
    - There is no `time` field for a `timed` subchallenge or a subchallenge with the time bonus enabled.
    """
    
    subchallenge_data = CHALLENGE_DATA[subchallenge["objective"]]
    
    for required in ["objective", "mode", "multiplier"]:
        if required not in subchallenge.keys():
            raise InvalidSubchallengeError(f"Subchallenge {subchallenge["objective"]} missing required field '{required}'.")
    
    if subchallenge["mode"] not in subchallenge_data["allowed_modes"]:
        allowed_modes = subchallenge_data["allowed_modes"]
        for i in range(len(allowed_modes)):
            allowed_modes[i] = f"'{allowed_modes[i]}'"
        raise InvalidSubchallengeError(f"Invalid mode {subchallenge["mode"]} for subchallenge {subchallenge["objective"]}. Valid modes are {', '.join(allowed_modes)}")
    
    if subchallenge["mode"] == "value":
        if "condition" not in subchallenge.keys():
            raise InvalidSubchallengeError(f"Subchallenge {subchallenge["objective"]} missing required field 'condition'.")
    
    subchallenge_has_time_bonus = "time_bonus_enabled" in subchallenge.keys() and subchallenge["time_bonus_enabled"]
    is_timed_challenge = subchallenge["mode"] == "timed"
    
    requires_time_field = subchallenge_has_time_bonus or is_timed_challenge
    if requires_time_field and "time" not in subchallenge.keys():
        raise InvalidSubchallengeError(f"No time specified for timed subchallenge {subchallenge["objective"]}")

    poker_hands = ["Pair", "Spectrum", "2 Pair", "3 of a Kind", "Full House", "4 of a Kind", "Flush"]
    if subchallenge["objective"] == "PokerHand" and subchallenge["extra"] not in poker_hands:
        raise InvalidSubchallengeError(f"No hand specified for subchallenge {subchallenge["objective"]}")

def load_challenge_json(json_string):
    contents: dict = json.loads(json_string)
    
    if "challenge_information" not in contents.keys():
        raise InvalidChallengeError("No metadata in challenge, fix by adding 'challenge_information' dictionary.")
    if "subchallenges" not in contents.keys():
        raise InvalidChallengeError("No subchallenges in challenge, fix by adding list of subchallenges under list 'subchallenges'.")
    
    metadata = contents["challenge_information"]
    check_challenge_metadata(metadata)
    
    subchallenges = []
    
    for subchallenge in contents["subchallenges"]:
        check_subchallenge_data(subchallenge)
        subchallenge_to_add = Subchallenge(subchallenge["objective"],
                                           subchallenge["mode"],
                                           subchallenge["multiplier"]
                                           )
        
        if "condition" in subchallenge.keys():
            subchallenge_to_add.condition = subchallenge["condition"]
        
        if "time_bonus_enabled" in subchallenge.keys():
            subchallenge_to_add.time_bonus_enabled = subchallenge["time_bonus_enabled"]
        
        if "time" in subchallenge.keys():
            subchallenge_to_add.time = subchallenge["time"]
        
        if "extra" in subchallenge.keys():
            subchallenge_to_add.extra = subchallenge["extra"]
        
        subchallenges += [subchallenge_to_add]
            
    return Challenge(metadata["name"],
                     metadata["author"],
                     metadata["description"],
                     metadata["mode"],
                     subchallenges,
                     time = metadata["time"] if "time" in metadata.keys() else None
                     )