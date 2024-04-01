from bj3wc import *
from gui import *

import multiprocessing

def main():
    gui = GraphicalUserInterface()
    world_championships = Bejeweled3WorldChampionships()
    
    with multiprocessing.Manager() as manager:
        gui_queue = manager.Queue()
        action_queue = manager.Queue()
        
        world_championships.gui_queue = gui_queue
        world_championships.action_queue = action_queue
        gui.gui_queue = gui_queue
        gui.action_queue = action_queue
        
        wc = multiprocessing.Process(target = world_championships.process_loop, name = "championships")
        
        wc.start()
        
        gui.start()
        
        while True:
            try:
                gui.root.winfo_exists()
            except:
                break
        
        wc.terminate()
        wc.close()
        print("World Championships stopped")
        
if __name__ == "__main__":
    main()