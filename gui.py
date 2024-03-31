import tkinter as tk
from tkinter import ttk, messagebox
from challenges import *

import queue, hashlib
from font import RenderFont
from PIL import ImageTk
from webbrowser import open as web_open

def get_from_resources(filename: str):
    return str(pathlib.Path(PATH, "resources", filename))

def insert_newlines(string, every): #thank you gurney alex (https://stackoverflow.com/questions/2657693/insert-a-newline-character-every-64-characters-using-python)
    return '-\n'.join(string[i:i+every] for i in range(0, len(string), every))

def sha256_sum(string_to_hash: str):
    if type(string_to_hash) != str: string_to_hash = str(string_to_hash)
    return hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()

class GraphicalUserInterface:
    def __init__(self):
        self.gui_queue = queue.Queue()     # Receives commands from BJ3WC (new challenges, scores, etc)
        self.action_queue = queue.Queue()  # Sends actions to BJ3WC (abort challenge, open new challenge, etc etc)
        self.font = RenderFont(get_from_resources("Flare Gothic Regular.ttf"))
        self.challenge: Challenge | None = None
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close())
        self.root.iconbitmap(get_from_resources("gem.ico"))
        self.root.resizable(False, False)
        
        self.size = tk.StringVar(value = "high") # Initialise GUI at "high" resolution
        self.show_time_left = tk.BooleanVar(value = False)
        
        self.set_up_menu_bar()
        self.set_resolution()
    
    def add_metadata_text(self):
        if self.challenge == None: return
        
        size = {"normal": 12,
                "high": 14,
                "ultra": 20
                }[self.size.get()]
        index = ["normal", "high", "ultra"].index(self.size.get())
        
        self.name_text = ImageTk.PhotoImage(self.font.get_render(size, self.challenge.name))
        self.canvas.create_image([(179, 35),
                                  (250, 44),
                                  (399, 69)
                                  ][index],
                                 image = self.name_text)
        self.author_text = ImageTk.PhotoImage(self.font.get_render(size, self.challenge.author))
        self.canvas.create_image([(179, 51),
                                  (250, 67),
                                  (399, 104)
                                  ][index],
                                 image = self.author_text)
        description = insert_newlines(self.challenge.description, 30)[:60] # Split every 30 characters, and trim after 60 characters
        self.description_text = ImageTk.PhotoImage(self.font.get_render(size, description, align = "la"))
        self.canvas.create_image([(121, 66),
                                  (155, 85),
                                  (243, 133)
                                  ][index],
                                 image = self.description_text)
        
        hash_text = f"Challenge hash:\n{sha256_sum(self.challenge.to_dict())}"
        self.challenge_hash_text = ImageTk.PhotoImage(self.font.get_render([7, 9, 12][index], hash_text, align = "mm"))
        self.canvas.create_image([(150, 470),
                                  (196, 601),
                                  (300, 940)
                                  ][index],
                                 image = self.challenge_hash_text)
    
    def close(self):
        # I know I could put the below into one if but that would be a long ass line of code.
        if self.challenge != None:
            if not messagebox.askyesno("Challenge in progress", "Are you sure you want to leave mid-challenge?"):
                return
        
        self.root.destroy()
        exit()
    
    def set_resolution(self):
        resolution = {"normal": "300x620",
                      "high": "384x788",
                      "ultra": "600x1220"}[self.size.get()]
        
        self.root.geometry(resolution)
        
        if self.size.get() == "ultra":
            self.root.title("Bejeweled 3 World Championships v0.2.0")
        else:
            self.root.title("BJ3WC v0.2.0")
        
        self.set_up_canvas(self.size.get())
        self.add_metadata_text()
        
    def set_up_canvas(self, size: str):
        self.background_image = tk.PhotoImage(file = get_from_resources(f"background_{size}.png"))
        
        match size:
            case "normal":
                canvas_size = {"width": 300, "height": 600}
                image_placement = (148, 300)
            case "high":
                canvas_size = {"width": 384, "height": 768}
                image_placement = (190, 384)
            case "ultra":
                canvas_size = {"width": 600, "height": 1200}
                image_placement = (298, 600)
        
        self.canvas = tk.Canvas(self.root,
                                **canvas_size,
                                background = "gray"
                                )
        self.canvas.place(x = 0, y = 20)
        self.canvas.create_image(image_placement,
                                 image = self.background_image
                                 )
        
    def set_up_menu_bar(self):
        file_button = ttk.Menubutton(self.root, text = "File")
        
        menu_file = tk.Menu(file_button, tearoff = False)
        menu_file.add_command(label = "Open",
                              underline = 0,
                              command = lambda: self.action_queue.put("open")
                              )
        
        submenu_resolution = tk.Menu(menu_file, tearoff = False)
        submenu_resolution.add_radiobutton(label='Normal (300x600)',
                                           value = "normal",
                                           variable = self.size,
                                           command = self.set_resolution,
                                           state = 'disabled'
                                           )
        submenu_resolution.add_radiobutton(label='High (384x768)',
                                           value = "high",
                                           variable = self.size,
                                           command = self.set_resolution
                                           )
        submenu_resolution.add_radiobutton(label='Ultra (600x1200)',
                                           value = "ultra",
                                           variable = self.size,
                                           command = self.set_resolution
                                           )
        
        menu_file.add_cascade(label = "Resolution", menu = submenu_resolution)
        menu_file.add_command(label = "Exit", underline = 0, command = lambda: self.close())
        
        file_button["menu"] = menu_file
        file_button.place(x = 0, y = 0)
        
        challenge_button = ttk.Menubutton(self.root, text = "Challenge")
        
        menu_challenge = tk.Menu(challenge_button, tearoff = False)
        menu_challenge.add_command(label = "Open",
                                   underline = 0,
                                   command = lambda: self.action_queue.put("open")
                                   )
        
        menu_challenge.add_command(label = "Abort",
                                   underline = 0,
                                   state = "disabled")
        
        menu_challenge.add_checkbutton(label = "Show time left",
                                       underline = 0,
                                       state = 'active',
                                       variable = self.show_time_left,
                                       onvalue = True,
                                       offvalue = False)
        
        challenge_button["menu"] = menu_challenge
        challenge_button.place(x = 60, y = 0)
        
        about_button = ttk.Menubutton(self.root, text = "About")
        
        menu_about = tk.Menu(about_button, tearoff = False)
        menu_about.add_command(label = "Challenge",
                               underline = 0)
        menu_about.add_command(label = "Documentation",
                               underline = 0,
                               command = lambda: web_open('about:blank'), # need to rewrite that
                               state = "disabled")
        menu_about.add_command(label = "GitHub page",
                               underline = 0,
                               command = lambda: web_open("https://github.com/redstone59/Bejeweled3WorldChampionships"))
        menu_about.add_command(label = "Find a bug?",
                               underline = 7,
                               command = lambda: web_open("https://github.com/redstone59/Bejeweled3WorldChampionships/issues"))
        
        about_button["menu"] = menu_about
        about_button.place(x = 150, y = 0)
    
    def start(self):
        self.root.mainloop()

g = GraphicalUserInterface()

c = Challenge("impossible challenge xviii", "Matthew :D", "impossible challenge, number 1 most impossible...", "timed", [], 40)
g.challenge = c
g.add_metadata_text()

g.start()