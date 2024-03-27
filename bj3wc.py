from bejeweled import *
from gui import *
from challenges import *

class Bejeweled3WorldChampionships:
    def __init__(self):
        self.challenge = None
        self.gui = GraphicalUserInterface()
        self.game = BejeweledThreeProcess()
        
        self.challenge_end_time = 0
        self.scores = []
    
    def get_score_pointer(self, subchallenge: Subchallenge):
        pointer_offsets = CHALLENGE_DATA[subchallenge.objective]["pointer_offsets"]
        
        for i in range(len(pointer_offsets)):
            try:
                pointer_offsets[i] = int(pointer_offsets[i], 0)
            except:
                continue
        
        return Pointer(self.game, *pointer_offsets)
    
    def open_challenge(self, challenge: Challenge):
        self.challenge = challenge
        print(challenge)
        
    def subchallenge_loop(self, subchallenge: Subchallenge):
        subchallenge_data: dict = CHALLENGE_DATA[subchallenge.objective]
        
        score_pointer = self.get_score_pointer(subchallenge)
        
        match subchallenge.mode:
            case "value":
                over_condition = lambda: score_pointer.get_value() >= subchallenge.condition
                if subchallenge.time_bonus_enabled:
                    subchallenge_end_time = time.time() + subchallenge.time
            case "timed":
                subchallenge_end_time = time.time() + subchallenge.time
                over_condition = lambda: time.time() >= subchallenge_end_time
            case "endless":
                over_condition = lambda: time.time() >= self.challenge_end_time
        
        while not over_condition():
            pass
    
    def start(self):
        if self.challenge == None:
            raise ValueError("No challenge has been loaded. Use Bejeweled3WorldChampionships().open_challenge()")
        
        if self.challenge.mode == "timed":
            self.challenge_end_time = time.time() + self.challenge.time
        
        while not self.challenge.is_over():
            subchallenge = self.challenge.next()
            print(subchallenge)
            self.wait_until_open(subchallenge)
            #self.subchallenge_loop(subchallenge)
    
    def wait_until_open(self, subchallenge: Subchallenge):
        """
        Blocks subchallenges from starting until the right mode is entered.
        """
        
        open_requirements = CHALLENGE_DATA[subchallenge.objective]["requirements"]
        
        if open_requirements["board_types"] == []:
            correct_board_type = lambda: self.game.get_board_type() != BoardType.UNKNOWN_BOARD
        else:
            correct_board_type = lambda: self.game.get_board_type().name in open_requirements["board_types"]
        
        if open_requirements["quest_ids"] == []:
            correct_quest_id = lambda: True
        else:
            correct_quest_id = lambda: self.game.get_quest_id() in open_requirements["quest_ids"]
        
        correct_game_open = lambda: correct_board_type() and correct_quest_id()
        
        if "initial_value" in open_requirements:
            initial_value = open_requirements["initial_value"]
        else:
            initial_value = 0
        
        score_pointer = self.get_score_pointer(subchallenge)
        score_reset = lambda: score_pointer.get_value() == initial_value
        new_game_started = lambda: correct_game_open() and score_reset
        
        while not new_game_started():
            score_pointer.update_address()