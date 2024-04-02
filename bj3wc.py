from bejeweled import *
from challenges import *
from queue_items import *

import queue

MINIQUEST_GOALS: list = json.load(open(pathlib.Path(PATH, "miniquest_goals.json")))

class Bejeweled3WorldChampionships:
    def __init__(self):
        self.challenge = None
        self.game = None
        self.gui_queue = queue.Queue()              # Sends actions to the GUI (scores, reset, etc)
        self.action_queue = queue.Queue()           # Receives actions from the GUI (opened challenge)
        
        self.challenge_end_time = 0
        self.penalty = 120
        self.scores = {}
        self.fail_type = None
    
    def add_subchallenge_extra(self, subchallenge: Subchallenge):
        if subchallenge.objective in ["Avalanche", "Balance", "Butterflies", "ButterClear", "ButterCombo", "MatchBomb", "TimeBomb"]:
            if subchallenge.objective == "Balance":
                extra_pointer = Pointer(self.game, 0xbe0, 0x323c)
            else:
                extra_pointer = Pointer(self.game, 0xbe0, 0x3238)
            
            if subchallenge.extra == None:          # Apply defaults
                match subchallenge.objective:
                    case "Avalanche":
                        extra_pointer.set_value(5)  # 5 gems fall per turn
                    
                    case "Balance":
                        extra_pointer.set_value(9)  # Fix gem scale speed.
                    
                    case "Butterflies" | "ButterClear" | "ButterCombo":
                        extra_pointer.set_value(1)  # Butterflies move up every match
                        
                    case "MatchBomb" | "TimeBomb":
                        extra_pointer.set_value(30) # Initial value for bombs is 30 turns or seconds.
            
            else:
                extra_pointer.set_value(subchallenge.extra)
    
    def do_subchallenge(self, subchallenge: Subchallenge):
        self.game.reset_scores()
        condition_pointer = self.get_condition_pointer(subchallenge)
        condition_pointer.update_address()
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
        
        if subchallenge.objective == "Stratamax":
            over_condition = lambda: Pointer(self.game, 0xbe0, 0x323c).get_value() <= 0
        
        score_pointer = self.get_score_pointer(subchallenge)
        get_score = lambda: score_pointer.get_value() - difference
        
        current_score = get_score()
        
        while not over_condition():
            score_pointer.update_address()
            previous_score = current_score
            current_score = get_score()
            
            if current_score < previous_score:
                print("Challenge failed! (game over or reset detected)")
                self.fail_type = "reset"
                
                if self.challenge.mode == "timed":
                    print(f"{self.penalty} second penalty!")
                    self.challenge_end_time -= self.penalty
                
                get_score = lambda: previous_score - difference
                break
            
            elif subchallenge.time_bonus_enabled:
                if subchallenge_end_time <= time.time():
                    print("Challenge failed! (time ran out)")
                    self.fail_type = "time out"
                    
                    if self.challenge.mode == "timed":
                        print(f"{self.penalty} second penalty!")
                        self.challenge_end_time -= self.penalty

                    break
            
            elif self.is_challenge_time_up():
                if len(self.challenge.subchallenges) != 0:
                    self.fail_type = "challenge end"
                break

        if subchallenge.time_bonus_enabled:
            get_score = lambda: int(subchallenge_end_time - time.time()) * 1000

        return max(0, get_score())
             
    def get_condition_pointer(self, subchallenge: Subchallenge):
        pointer_offsets = CHALLENGE_DATA[subchallenge.objective]["pointer_offsets"]
        
        if subchallenge.objective == "PokerHand":
            poker_hands = ["Pair", "Spectrum", "2 Pair", "3 of a Kind", "Full House", "4 of a Kind", "Flush"]
            return Pointer(self.game, 0xbe0, 0x39d8 + 4 * poker_hands.index(subchallenge.extra))
        
        for i in range(len(pointer_offsets)):
            try:
                pointer_offsets[i] = int(pointer_offsets[i], 0)
            except:
                continue

        return Pointer(self.game, *pointer_offsets)
    
    def get_score_pointer(self, subchallenge: Subchallenge):
        quest_challenges = ["DiamondMine", "DiamondDepth", "DiamondTreasure",
                            "Balance", "Stratamax", "GoldRush", "Alchemy",
                            "TimeBomb", "MatchBomb", "Avalanche", "WallBlast",
                            "Treasure", "Sand"
                            ]
        if subchallenge.objective not in quest_challenges:
            score_pointer = Pointer(self.game, 0xbe0, 0xd20)
        else:
            score_pointer = Pointer(self.game, 0xbe0, 0xe00)
        
        return score_pointer
    
    def is_challenge_time_up(self):
        if self.challenge.mode == "marathon": return False
        return time.time() >= self.challenge_end_time
    
    def modify_quest_goals(self, subchallenge: Subchallenge):
        difference = None
        
        match subchallenge.objective:
            case "Avalanche":
                if subchallenge.mode == "value":
                    difference = MINIQUEST_GOALS[self.game.get_quest_id()] - subchallenge.condition
                else:
                    difference = -1000
                Pointer(self.game, 0xbe0, 0xe00).set_value(difference)
            
            case "Balance":
                balance_amount = (subchallenge.condition // 2) if subchallenge.mode == "value" else 34710
                Pointer(self.game, 0xbe0, 0x3238).set_value(balance_amount) # Set BalanceGoal
            
            case "BuriedTreasure" | "GoldRush" | "Sandstorm" | "WallBlast":
                Pointer(self.game, 0xbe0, 0x3238).set_value(1800)           # Set time left to 30 minutes
            
            case "Poker" | "PokerLimit" | "PokerHand" | "PokerSkull":
                if self.game.get_quest_id() != 1000:                        # This will never be met - Poker quests only start on the secret Poker mode.
                    Pointer(self.game, 0xbe0, 0x323c).set_value(100000)     # Set PokerGoal to absurdly high number
                    Pointer(self.game, 0xbe0, 0x395c).set_value(1000)       # Change number of hands remaining to 1000
            
            case "TimeBomb" | "MatchBomb":
                if subchallenge.mode == "value":
                    difference = MINIQUEST_GOALS[self.game.get_quest_id()] - subchallenge.condition
                else:
                    difference = -1000
                Pointer(self.game, 0xbe0, 0xe00).set_value(difference)
            
            case "Stratamax":
                difference = -1000
                Pointer(self.game, 0xbe0, 0xe00).set_value(difference) 
                Pointer(self.game, 0xbe0, 0x3238).set_value(subchallenge.condition)
                Pointer(self.game, 0xbe0, 0x323c).set_value(subchallenge.condition)
        
        return difference
    
    def open_challenge(self, challenge: Challenge):
        self.challenge = challenge

    def process_loop(self):
        running = True
        
        self.game = BejeweledThreeProcess() # Fixes worlds strangest bug (pointers dont read if the game isnt found inside of the process)
        self.gui_queue.put(QueueItem("game_opened"))
        
        while running:
            if self.action_queue.empty(): continue
            action: QueueItem = self.action_queue.get()
            
            match action.function:
                case "abort":
                    running = False
                case "open":
                    self.open_challenge(action.arguments[0])
                case "start":
                    self.start()
    
    def start(self):
        if self.challenge == None:
            raise ValueError("No challenge has been loaded. Use Bejeweled3WorldChampionships().open_challenge()")
        
        if self.challenge.mode == "timed":
            self.challenge_end_time = time.time() + self.challenge.time
        
        self.scores = {}
        
        self.subchallenge_loop()
        print("Time!")
        
        add_and_display_scores(self.scores)
        self.gui_queue.put(QueueItem("challenge_end", self.scores))

    def subchallenge_loop(self): 
        while not (self.challenge.is_over() or self.is_challenge_time_up()):
            subchallenge = self.challenge.next()
            
            print(subchallenge)
            self.gui_queue.put(QueueItem("subchallenge", subchallenge.get_gui_string(), str(subchallenge)))
            
            if subchallenge.objective in ["ClasLevel", "ZenLevel"]: # Zero-indexed internally, One-indexed externally
                subchallenge.condition -= 1
            
            dordle_time = time.time()
            self.wait_until_open(subchallenge)
            time.sleep(0.5)
            
            if self.challenge.mode == "timed":
                self.challenge_end_time += time.time() - dordle_time
                self.gui_queue.put(QueueItem("new_end_time", self.challenge_end_time))
            
            print("Go!")
            self.fail_type = None
            
            final_score = self.do_subchallenge(subchallenge)
            
            if self.fail_type != None:
                self.gui_queue.put(QueueItem("score", final_score, self.fail_type))
            else:
                self.gui_queue.put(QueueItem("score", final_score))
            
            self.scores[subchallenge.objective] = {"multiplier": subchallenge.multiplier, "score": final_score}
    
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
        new_game_started = lambda: correct_game_open() and score_reset()
        
        while not new_game_started():
            condition_pointer.update_address()

def add_and_display_scores(challenge_dict: dict):
    total_score = 0
    print("---------------")
    
    for key in challenge_dict:
        subchallenge = challenge_dict[key]
        print(f"{key}: {subchallenge["score"]:,} * {subchallenge["multiplier"]:,} = {subchallenge["score"] * subchallenge["multiplier"]:,}")
        total_score += subchallenge["score"] * subchallenge["multiplier"]
    
    print("---------------")
    print(f"TOTAL SCORE: {total_score:,}")
    print("---------------")