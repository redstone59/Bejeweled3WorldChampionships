import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from challenges import *
from queue_items import *

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
        self.gui_queue = queue.Queue()           # Receives commands from BJ3WC (new challenges, scores, etc)
        self.action_queue = queue.Queue()        # Sends actions to BJ3WC (abort challenge, open new challenge, etc etc)
        self.font = RenderFont(get_from_resources("Flare Gothic Regular.ttf"))
        self.challenge: Challenge | None = None
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close())
        self.root.iconbitmap(get_from_resources("gem.ico"))
        self.root.resizable(False, False)
        
        self.size = tk.StringVar(value = "high") # Initialise GUI at "high" resolution
        self.show_time_left = tk.BooleanVar(value = False)
        self.index = 0
        
        self.reset_labels()
        self.set_up_menu_bar()
        self.set_resolution()
    
    def add_subchallenge_score(self, score: int):
        text_position = {"normal": (38, 148 + 35 * self.index), # Estimated vertical offset
                         "high": (49, 190 + 46 * self.index),
                         "ultra": (76, 297 + 72 * self.index)
                         }[self.size.get()]
        size = {"normal": 15,
                "high": 19,
                "ultra": 30
                }[self.size.get()]
        
        self.labels["scores"] += [ImageTk.PhotoImage(self.font.get_render(size, f"{score:,}", colour = "#f4f4d0", align = "ls"))]
        self.canvas.create_image(text_position, image = self.labels["scores"][-1])
        
        self.index += 1
    
    def add_subchallenge_text(self, text: str):
        text_position = {"normal": (38, 130 + 35 * self.index), # Estimated vertical offset
                         "high": (49, 167 + 46 * self.index),
                         "ultra": (76, 261 + 72 * self.index)
                         }[self.size.get()]
        size = {"normal": 15,
                "high": 19,
                "ultra": 30
                }[self.size.get()]
        
        self.labels["challenges"] += [ImageTk.PhotoImage(self.font.get_render(size, text, colour = "#f4f4d0", align = "ls"))]
        self.canvas.create_image(text_position, image = self.labels["challenges"][-1])
    
    def add_multiplied_scores(self, scores: dict):
        size = {"normal": 15,
                "high": 19,
                "ultra": 30
                }[self.size.get()]
        
        self.index = 0
        final_score = 0
        
        for key in scores:
            multiplier_position = {"normal": (262, 130 + 35 * self.index), # Estimated vertical offset
                                   "high": (336, 167 + 46 * self.index),
                                   "ultra": (526, 261 + 72 * self.index)
                                   }[self.size.get()]
            score_position = {"normal": (262, 148 + 35 * self.index), # Estimated vertical offset
                              "high": (336, 190 + 46 * self.index),
                              "ultra": (526, 297 + 72 * self.index)
                              }[self.size.get()]
            score = scores[key]
            
            self.labels["multipliers"] += [ImageTk.PhotoImage(self.font.get_render(size, f"x{score["multiplier"]:,}", colour = "#ffff60", align = "rs"))]
            self.canvas.create_image(multiplier_position, image = self.labels["multipliers"][-1])
            
            self.labels["multiplied_scores"] += [ImageTk.PhotoImage(self.font.get_render(size, f"{score["score"] * score["multiplier"]:,}", colour = "#ffff60", align = "rs"))]
            self.canvas.create_image(score_position, image = self.labels["multiplied_scores"][-1])
            
            final_score += score["score"] * score["multiplier"]
            self.index += 1
        
        final_score_position = {"normal": (150, 555),
                                "high": (196, 710),
                                "ultra": (300, 1110),
                                }[self.size.get()]
        size = {"normal": 30,
                "high": 42,
                "ultra": 54
                }[self.size.get()]
        
        self.labels["multiplied_scores"] += [ImageTk.PhotoImage(RenderFont(get_from_resources("Myriad Pro Regular.OTF")).get_render(size, f"{final_score:,}"))]
        self.canvas.create_image(final_score_position, image = self.labels["multiplied_scores"][-1])
    
    def add_metadata_text(self):
        if self.challenge == None: return
        
        size = {"normal": 10,
                "high": 13,
                "ultra": 20
                }[self.size.get()]
        index = ["normal", "high", "ultra"].index(self.size.get())
        
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render(size, self.challenge.name))]
        self.canvas.create_image([(179, 35),
                                  (250, 44),
                                  (399, 69)
                                  ][index],
                                 image = self.labels["metadata"][-1])
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render(size, self.challenge.author))]
        self.canvas.create_image([(179, 51),
                                  (250, 67),
                                  (399, 104)
                                  ][index],
                                 image = self.labels["metadata"][-1])
        description = insert_newlines(self.challenge.description, 30)[:60] # Split every 30 characters, and trim after 60 characters
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render(size, description, align = "la"))]
        self.canvas.create_image([(121, 66),
                                  (155, 85),
                                  (243, 133)
                                  ][index],
                                 image = self.labels["metadata"][-1])
        
        hash_text = f"Challenge hash:\n{sha256_sum(self.challenge.to_dict())}"
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render([7, 9, 12][index], hash_text, align = "mm"))]
        self.canvas.create_image([(150, 470),
                                  (196, 601),
                                  (300, 940)
                                  ][index],
                                 image = self.labels["metadata"][-1])
    
    def check_queue(self):
        while not self.gui_queue.empty():
            action: QueueItem = self.gui_queue.get()
            
            match action.function:
                case _:
                    pass
    
    def close(self):
        # I know I could put the below into one if statement but that would be a long ass line of code.
        if self.challenge != None:
            if not messagebox.askyesno("Challenge in progress", "Are you sure you want to leave mid-challenge?"):
                return
        
        self.root.destroy()
        self.gui_queue.put("abort")
#       exit()
    
    def open_challenge_file(self):
        while True:
            challenge_file = filedialog.askopenfilename(parent = self.root, title = "Open challenge file", filetypes = [("JSON file", ".json")])
            
            try:
                with open(challenge_file) as file:
                    challenge = load_challenge_json(file.read())
                
                self.challenge = challenge
                self.reset_labels()
                self.add_metadata_text()
                break
                
            except (InvalidChallengeError, InvalidSubchallengeError, FileNotFoundError) as e:
                print(f"{e.__class__}: {e}")
                messagebox.showerror("Uh oh!", f"Invalid challenge chosen!\n{e.__class__}: {e}")
        
        self.action_queue.put(QueueItem("open", challenge))
        return challenge
    
    def reset_labels(self):
        self.labels = {"scores": [],
                       "challenges": [],
                       "multipliers": [],
                       "multiplied_scores": [],
                       "metadata": []}
    
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
                              command = lambda: self.open_challenge_file()
                              )
        
        submenu_resolution = tk.Menu(menu_file, tearoff = False)
        submenu_resolution.add_radiobutton(label = 'Normal (300x600)',
                                           value = "normal",
                                           variable = self.size,
                                           command = self.set_resolution,
                                           )
        submenu_resolution.add_radiobutton(label = 'High (384x768)',
                                           value = "high",
                                           variable = self.size,
                                           command = self.set_resolution
                                           )
        submenu_resolution.add_radiobutton(label = 'Ultra (600x1200)',
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
                                   command = lambda: self.open_challenge_file()
                                   )
        
        menu_challenge.add_command(label = "Abort",
                                   underline = 0,
                                   state = "disabled"
                                   )
        
        menu_challenge.add_checkbutton(label = "Show time left",
                                       underline = 0,
                                       state = 'active',
                                       variable = self.show_time_left,
                                       onvalue = True,
                                       offvalue = False
                                       )
        
        challenge_button["menu"] = menu_challenge
        challenge_button.place(x = 60, y = 0)
        
        about_button = ttk.Menubutton(self.root, text = "About")
        
        menu_about = tk.Menu(about_button, tearoff = False)
        menu_about.add_command(label = "Challenge",
                               underline = 0
                               )
        menu_about.add_command(label = "Documentation",
                               underline = 0,
                               command = lambda: web_open('about:blank'), # need to rewrite that
                               state = "disabled"
                               )
        menu_about.add_command(label = "GitHub page",
                               underline = 0,
                               command = lambda: web_open("https://github.com/redstone59/Bejeweled3WorldChampionships")
                               )
        menu_about.add_command(label = "Find a bug?",
                               underline = 7,
                               command = lambda: web_open("https://github.com/redstone59/Bejeweled3WorldChampionships/issues")
                               )
        
        about_button["menu"] = menu_about
        about_button.place(x = 150, y = 0)
    
    def start(self):
        self.root.mainloop()

g = GraphicalUserInterface()

c = Challenge("Challenge E", "redstone59", "Non-timed challenge included with BJ3WC", "timed", [], 40)
g.challenge = c
g.add_metadata_text()
g.size.set("high")
g.set_resolution()
g.add_subchallenge_text("Lightning: 45s in tank")
g.add_subchallenge_score(52350)
g.add_subchallenge_text("Poker: 10 hands")
g.add_subchallenge_score(185750)
g.add_subchallenge_text("Match Bomb: 8 bombs (60s) [15]")
g.add_subchallenge_score(56976)
g.add_multiplied_scores({"a": {"multiplier": 1, "score": 52350}, "b": {"multiplier": 3, "score": 185750}, "c": {"multiplier": 5, "score": 56976}})

g.start()