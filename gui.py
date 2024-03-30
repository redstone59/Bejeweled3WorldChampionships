import tkinter as tk
from tkinter import ttk
from challenges import *

import queue
from tkextrafont import Font

class GraphicalUserInterface:
    def __init__(self):
        self.gui_queue = queue.Queue()
        self.root = tk.Tk()
        self.root.geometry = "384x788"
        self.root.title = "Bejeweled 3 World Championships v0.2.0"