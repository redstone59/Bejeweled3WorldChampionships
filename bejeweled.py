from ReadWriteMemory import ReadWriteMemory, ReadWriteMemoryError
import time

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
    
    def write(self, offsets: tuple[int], value: int):
        if type(offsets) == int: offsets = (offsets,)
        self.process.write(self.read(*offsets), value)
        
class Pointer:
    def __init__(self, process: BejeweledThreeProcess, *offsets: tuple[int]):
        if type(offsets) == int: offsets = (offsets,)
        self.process = process
        self.address = process.read(*offsets[:-1]) + offsets[-1]
        self.offsets = offsets
    
    def get_value(self):
        return self.process.process.read(self.address)
    
    def update_address(self):
        self.address = self.process.read(*self.offsets[:-1]) + self.offsets[-1]
    
    def set_value(self, value: int):
        if type(value) != int: raise TypeError("Pointer values can only be ints.")
        return self.process.process.write(self.address, value)
    
    def __set__(self, value: int):
        self.set_value(value)