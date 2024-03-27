from ReadWriteMemory import ReadWriteMemory, ReadWriteMemoryError
import time
from enum import Enum

class BoardType(Enum):
    # Names taken from the Bejeweled 3 Extender, different values because this isn't 3 Plus.
    # https://github.com/bognarit80/Bejeweled3PlusExtender/blob/main/3PlusExtensions/mods/gamefunctions.h
    UNKNOWN_BOARD = 0
    BOARD = 0x800000 # I just ANDed all the below enums to get this. Probably won't use it.
    CLASSIC_BOARD = 0x80d644
    SPEED_BOARD = 0x80eabc
    ZEN_BOARD = 0x80f05c
    QUEST_BOARD = 0x800004 # I just ANDed all the below enums to get this. Probably won't use it.
    DIG_BOARD = 0x80dcd4
    BALANCE_BOARD = 0x80fd7c
    BUTTERFLY_BOARD = 0x8101e4
    FILLER_BOARD = 0x81064c
    MOVE_LIMIT_BOARD = 0x810f4c
    NO_LOSE_BOARD = 0x810ab4
    POKER_BOARD = 0x81181c
    REAL_TIME_BOMB_BOARD = 0x81226c
    TIME_BOMB_BOARD = 0x81226c
    TIME_LIMIT_BOARD = 0x8126d4

class BejeweledThreeProcess:
    def __init__(self):
        print("Attempting to find Bejeweled 3...")
        not_open = True
        while not_open:
            try:
                self.process = ReadWriteMemory().get_process_by_name("popcapgame1.exe")
                self.process.open()
                # I have no clue what 'addr' meant in the original repo. Is it some base address? Is 'base address' even a term?
                self.address = self.process.read(0x887f34) # I don't know why it was split before, but it was 0x400000 + 0x487f34, so,
                print("Bejeweled 3 found!")
                not_open = False
            except ReadWriteMemoryError:
                print("Bejeweled 3 not found! Trying again in 1 second...")
                time.sleep(1)
    
    def read(self, *offsets: int):
        if type(offsets) == int: offsets = (offsets,)
        result = self.address
        
        for offset in offsets:
            result = self.process.read(result + offset)
        
        return result
    
    def reset_scores(self):
        Pointer(self, 0xbe0, 0xd20).set_value(0)
        Pointer(self, 0xbe0, 0xe00).set_value(0)
    
    def write(self, offsets: tuple[int], value: int):
        if type(offsets) == int: offsets = (offsets,)
        self.process.write(self.read(*offsets), value)
        
    def get_board_type(self):
        try:
            return BoardType(Pointer(self, 0xbe0, 0x0).get_value())
        except ValueError:
            return None
    
    def get_score(self):
        return Pointer(self, 0xbe0, 0xd20).get_value()
    
    def get_level(self):
        return Pointer(self, 0xbe0, 0xe04).get_value() + 1 # Levels start at 0
    
    def get_quest_id(self):
        return Pointer(self, 0xbe0, 0x322c).get_value()
    
    def get_quest_goal_type(self):
        pass
    
    def get_quest_requirement(self):
        pass
        
class Pointer:
    def __init__(self, process: BejeweledThreeProcess, *offsets: tuple[int]):
        if type(offsets) == int: offsets = (offsets,)
        self.process = process
        self.address = process.read(*offsets[:-1]) + offsets[-1]
        self.offsets = offsets
    
    def get_value(self):
        return self.process.process.read(self.address)
    
    read = get_value
    
    def update_address(self):
        self.address = self.process.read(*self.offsets[:-1]) + self.offsets[-1]
    
    def set_value(self, value: int):
        if type(value) != int: raise TypeError("Pointer values can only be ints.")
        self.process.process.write(self.address, value)
    
    def __set__(self, value: int):
        self.set_value(value)