from dataclasses import *
from typing import Literal
import json

CHALLENGE_DATA = json.load(open("./challenges.json"))

class InvalidChallengeError(Exception):
    pass

class InvalidSubchallengeError(Exception):
    pass

@dataclass
class Subchallenge:
    objective: str
    mode: str
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
        result["condition"] = self.condition
        
        if self.time_bonus_enabled: result["time_bonus"] = True
        if self.time != None: result["time"] = self.time
        if self.extra != None: result["extra"] = self.extra
        
        result["multiplier"] = self.multiplier

@dataclass
class Challenge:
    name: str
    author: str
    description: str
    mode: Literal["timed", "marathon"]
    subchallenges: list[Subchallenge]
    time: int | None = None
    
    def next(self):
        if len(self.subchallenges) == 0: return None
        return self.subchallenges.pop(0)

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

def load_challenge_json(json_string):
    contents = json.loads(json_string)
    if len(contents) != 2: raise InvalidChallengeError("Invalid challenge JSON.")
    metadata = contents[0]
    check_challenge_metadata(metadata)
    
    subchallenges = []
    
    for subchallenge in contents[1]:
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
        
        subchallenges += [subchallenge_to_add]
            
    return Challenge(metadata["name"],
                     metadata["author"],
                     metadata["description"],
                     metadata["mode"],
                     subchallenges,
                     time = metadata["time"] if "time" in metadata.keys() else None
                     )