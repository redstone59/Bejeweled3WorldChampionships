from multiprocessing import Process, Manager, freeze_support

def main():
    VER = "1.0-prerelease"
    gui = GraphicalUserInterface(VER)
    world_championships = Bejeweled3WorldChampionships()
    
    with Manager() as manager:
        gui_queue = manager.Queue()
        action_queue = manager.Queue()
        
        world_championships.gui_queue = gui_queue
        world_championships.action_queue = action_queue
        gui.gui_queue = gui_queue
        gui.action_queue = action_queue
        
        wc = Process(target = world_championships.process_loop, name = "championships")
        
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
    freeze_support() # This should make Pyinstaller not launch the program multiple times.
    from bj3wc import *
    from gui import *
    main()