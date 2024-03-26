import tkinter as tk
from tkinter import ttk

import queue

class GraphicalUserInterface:
    def __init__(self):
        self.gui_queue = queue.Queue()