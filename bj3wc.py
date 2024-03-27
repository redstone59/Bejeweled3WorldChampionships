from bejeweled import *
from gui import *
from challenges import *

MINIQUEST_GOALS: list = json.load(open("./miniquest_goals.json"))

class Bejeweled3WorldChampionships:
    def __init__(self):
        self.challenge = None
        self.gui = GraphicalUserInterface()
        self.game = BejeweledThreeProcess()
        
        self.challenge_end_time = 0
        self.scores = []
    
    def add_subchallenge_extra(self, subchallenge: Subchallenge):
        if subchallenge.objective in ["Avalanche", "Butterflies", "ButterClear", "ButterCombo", "MatchBomb", "TimeBomb"]:
            extra_pointer = Pointer(self.game, 0xbe0, 0x3238)
            
            if subchallenge.extra == None: # Apply defaults
                match subchallenge.objective:
                    case "Avalanche":
                        extra_pointer.set_value(5) # 5 gems fall per turn
                        
                    case "Butterflies" | "ButterClear" | "ButterCombo":
                        extra_pointer.set_value(1) # Butterflies move up every match
                        
                    case "MatchBomb" | "TimeBomb":
                        extra_pointer.set_value(30) # Initial value for bombs is 30 turns or seconds.
            
            else:
                extra_pointer.set_value(subchallenge.extra)
    
    def is_challenge_time_up(self):
        if self.challenge.mode == "marathon": return False
        return time.time() >= self.challenge_end_time
    
    def modify_quest_goals(self, subchallenge: Subchallenge):
        difference = None
        
        match subchallenge.objective:
            case "Avalanche":
                difference = MINIQUEST_GOALS[self.game.get_quest_id()] - subchallenge.condition
                Pointer(self.game, 0xbe0, 0xe00).set_value(difference)
            
            case "Balance":
                balance_amount = (subchallenge.condition // 2) if subchallenge.mode == "value" else 34710
                Pointer(self.game, 0xbe0, 0x3238).set_value(balance_amount) # Set BalanceGoal
                Pointer(self.game, 0xbe0, 0x323c).set_value(9) # Fix speed (could probably make this an extra tbh)
            
            case "BuriedTreasure" | "GoldRush" | "Sandstorm" | "WallBlast":
                Pointer(self.game, 0xbe0, 0x3238).set_value(1800) # Set time to 30 minutes
            
            case "Poker" | "PokerLimit" | "PokerHand" | "PokerSkull":
                if self.game.get_quest_id() != 1000:
                    Pointer(self.game, 0xbe0, 0x323c).set_value(100000)
                    Pointer(self.game, 0xbe0, 0x395c).set_value(1000)
            
            case "TimeBomb" | "MatchBomb":
                difference = -1000
                Pointer(self.game, 0xbe0, 0xe00).set_value(difference)
            
            case "Stratamax":
                Pointer(self.game, 0xbe0, 0x3238).set_value(subchallenge.condition)
                Pointer(self.game, 0xbe0, 0x323c).set_value(subchallenge.condition)
        
        return difference
             
    def get_condition_pointer(self, subchallenge: Subchallenge):
        pointer_offsets = CHALLENGE_DATA[subchallenge.objective]["pointer_offsets"]
        
        if subchallenge.objective == "PokerHand":
            poker_hands = ["Pair", "Spectrum", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind", "Flush"]
            return Pointer(0xbe0, 0x39d8 + 4 * poker_hands.index(subchallenge.extra))
        
        for i in range(len(pointer_offsets)):
            try:
                pointer_offsets[i] = int(pointer_offsets[i], 0)
            except:
                continue
        
        return Pointer(self.game, *pointer_offsets)
    
    def get_score_pointer(self, subchallenge: Subchallenge):
        if subchallenge.objective not in ["DiamondMine", "DiamondDepth", "DiamondTreasure"]:
            score_pointer = Pointer(self.game, 0xbe0, 0xd20)
        else:
            score_pointer = Pointer(self.game, 0xbe0, 0xe00)
        
        return score_pointer
    
    def open_challenge(self, challenge: Challenge):
        self.challenge = challenge
        print(challenge)
        
    def subchallenge_loop(self, subchallenge: Subchallenge):
        self.game.reset_scores()
        condition_pointer = self.get_condition_pointer(subchallenge)
        condition_pointer.set_value(subchallenge.get_initial_value()) # Reset checked value
        
        difference = self.modify_quest_goals(subchallenge)
        if difference == None: difference = 0
        
        self.add_subchallenge_extra(subchallenge)
        
        match subchallenge.mode:
            case "value":
                over_condition = lambda: condition_pointer.get_value() >= subchallenge.condition + difference
                if subchallenge.time_bonus_enabled:
                    subchallenge_end_time = time.time() + subchallenge.time
            case "timed":
                subchallenge_end_time = time.time() + subchallenge.time
                over_condition = lambda: time.time() >= subchallenge_end_time
            case "endless":
                over_condition = lambda: time.time() >= self.challenge_end_time
        
        while not (over_condition() or self.is_challenge_time_up()):
            pass
    
    def start(self):
        if self.challenge == None:
            raise ValueError("No challenge has been loaded. Use Bejeweled3WorldChampionships().open_challenge()")
        
        if self.challenge.mode == "timed":
            self.challenge_end_time = time.time() + self.challenge.time
        
        while not self.challenge.is_over():
            subchallenge = self.challenge.next()
            
            score_pointer = self.get_score_pointer(subchallenge)
            print(subchallenge)
            
            self.wait_until_open(subchallenge)
            time.sleep(0.5)
            print("go!")
            
            self.subchallenge_loop(subchallenge)
            
            self.scores += score_pointer.get_value()
        
        print(self.scores)
    
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
        initial_value = subchallenge.get_initial_value()
        
        condition_pointer = self.get_condition_pointer(subchallenge)
        score_reset = lambda: condition_pointer.get_value() == initial_value
        new_game_started = lambda: correct_game_open() and score_reset
        
        while not new_game_started():
            condition_pointer.update_address()
