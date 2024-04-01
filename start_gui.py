from bj3wc import *
from gui import *

import multiprocessing

def main():
    world_championships = Bejeweled3WorldChampionships()
    gui = GraphicalUserInterface()
    
    with multiprocessing.Manager() as manager:
        gui_queue = manager.Queue()
        action_queue = manager.Queue()
        
        world_championships.gui_queue = gui_queue
        world_championships.action_queue = action_queue
        gui.gui_queue = gui_queue
        gui.action_queue = action_queue
        
        wc = multiprocessing.Process(target = world_championships.check_queue, name = "championships")
        
        wc.start()
        
        gui.start()
        wc.join()
        print("World Championships stopped")
        

if __name__ == "__main__":
    main()