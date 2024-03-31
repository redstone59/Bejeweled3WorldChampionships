from dataclasses import *

@dataclass
class QueueItem:
    function: str
    arguments: tuple | list
    
    def __post_init__(self):
        if type(self.arguments) not in [tuple, list]:
            try:
                self.arguments = tuple(self.arguments,)
            except:
                self.arguments = (self.arguments,)