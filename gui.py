import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from challenges import *
from queue_items import *

import queue, hashlib, time
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
        self.pester_about_game = True
        
        self.reset_labels()
        self.set_up_menu_bar()
        self.set_resolution()
    
    def add_subchallenge_score(self, score: int, fail_type = ""):
        text_position = {"normal": (38, 148 + 35 * self.index), # Estimated vertical offset
                         "high": (49, 190 + 46 * self.index),
                         "ultra": (76, 297 + 72 * self.index)
                         }[self.size.get()]
        size = {"normal": 15,
                "high": 19,
                "ultra": 30
                }[self.size.get()]
        
        score_string = f"{score:,}"
        if fail_type != "":
            score_string += f" ({fail_type})"
        
        self.labels["scores"] += [ImageTk.PhotoImage(self.font.get_render(size, score_string, colour = "#f4f4d0", align = "ls"))]
        self.canvas.create_image(text_position, image = self.labels["scores"][-1], tags = "game")
        
        self.index += 1
    
    def add_subchallenge_text(self, abbreviated_text: str, description_text: str):
        text_position = {"normal": (38, 130 + 35 * self.index), # Estimated vertical offset
                         "high": (49, 167 + 46 * self.index),
                         "ultra": (76, 261 + 72 * self.index)
                         }[self.size.get()]
        size = {"normal": 15,
                "high": 19,
                "ultra": 30
                }[self.size.get()]
        
        self.labels["challenges"] += [ImageTk.PhotoImage(self.font.get_render(size, abbreviated_text, colour = "#f4f4d0", align = "ls"))]
        self.canvas.create_image(text_position, image = self.labels["challenges"][-1], tags = "game")
        
        text_position = {"normal": (150, 592),
                         "high": (196, 758),
                         "ultra": (300, 1185)
                         }[self.size.get()]
        size = {"normal": 8,
                "high": 10,
                "ultra": 16
                }[self.size.get()]
        
        self.canvas.delete("current_quest")
        self.labels["current_quest"] = ImageTk.PhotoImage(self.font.get_render(size, description_text))
        self.canvas.create_image(text_position, image = self.labels["current_quest"], tags = "current_quest")
    
    def add_multiplied_scores(self, scores: dict):
        self.canvas.delete("current_quest")
        
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
            self.canvas.create_image(multiplier_position, image = self.labels["multipliers"][-1], tags = "game")
            
            self.labels["multiplied_scores"] += [ImageTk.PhotoImage(self.font.get_render(size, f"{score["score"] * score["multiplier"]:,}", colour = "#ffff60", align = "rs"))]
            self.canvas.create_image(score_position, image = self.labels["multiplied_scores"][-1], tags = "game")
            
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
                                 image = self.labels["metadata"][-1],
                                 tags = "game"
                                 )
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render(size, self.challenge.author))]
        self.canvas.create_image([(179, 51),
                                  (250, 67),
                                  (399, 104)
                                  ][index],
                                 image = self.labels["metadata"][-1],
                                 tags = "game"
                                 )
        description = insert_newlines(self.challenge.description, 30)[:60] # Split every 30 characters, and trim after 60 characters
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render(size, description, align = "la"))]
        self.canvas.create_image([(121, 66),
                                  (155, 85),
                                  (243, 133)
                                  ][index],
                                 image = self.labels["metadata"][-1],
                                 tags = "game"
                                 )
        
        hash_text = f"Challenge hash:\n{sha256_sum(self.challenge.to_dict())}"
        self.labels["metadata"] += [ImageTk.PhotoImage(self.font.get_render([7, 9, 12][index], hash_text, align = "mm"))]
        self.canvas.create_image([(150, 470),
                                  (196, 601),
                                  (300, 940)
                                  ][index],
                                 image = self.labels["metadata"][-1],
                                 tags = "game"
                                 )
    
    def check_queue(self):
        while not self.gui_queue.empty():
            action: QueueItem = self.gui_queue.get()
            
            match action.function:
                case "challenge_end":
                    self.add_multiplied_scores(action.arguments[0])
                    self.challenge = None
                    self.update_menu_states(False)
                case "game_opened":
                    self.pester_about_game = False
                case "score":
                    self.add_subchallenge_score(*action.arguments)
                case "subchallenge":
                    self.add_subchallenge_text(*action.arguments)
                case "new_end_time":
                    self.challenge_end_time = action.arguments[0]
                    self.update_time_display()
            
            self.root.update()
        
        if self.pester_about_game:
            clicked_retry = messagebox.showerror("Uh oh!",
                                                 "Bejeweled 3 not detected! Please open the game and press Retry, otherwise hit Cancel to close the program.",
                                                 type = messagebox.RETRYCANCEL
                                                 ) == "retry"
            if not clicked_retry:
                self.close()
        
        self.update_time_display()
        self.root.after(100, self.check_queue)
    
    def close(self):
        # I know I could put the below into one if statement but that would be a long ass line of code.
        if self.challenge != None:
            if not messagebox.askyesno("Challenge in progress", "Are you sure you want to leave mid-challenge?"):
                return
        
        self.root.destroy()
        self.action_queue.put(QueueItem("abort", ()))
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
                
                if self.challenge.mode == "timed":
                    self.challenge_end_time = time.time() + self.challenge.time
                
                break
                
            except (InvalidChallengeError, InvalidSubchallengeError, FileNotFoundError) as e:
                print(f"{e.__class__}: {e}")
                messagebox.showerror("Uh oh!", f"Invalid challenge chosen!\n{e.__class__}: {e}")
                return

        self.index = 0
        self.action_queue.put(QueueItem("open", challenge))
        self.action_queue.put(QueueItem("start", ()))
        self.update_menu_states(True)
        self.toggle_time_display()
        return challenge
    
    def reset_labels(self):
        self.labels = {"scores": [],
                       "challenges": [],
                       "multipliers": [],
                       "multiplied_scores": [],
                       "metadata": [],
                       "timer": tk.Label(self.root, text = "0:00", font = ("Arial", 10))
                       }
    
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
        self.toggle_time_display()
        
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
        
        self.menu_file = tk.Menu(file_button, tearoff = False)
        self.menu_file.add_command(label = "Open",
                                   underline = 0,
                                   command = lambda: self.open_challenge_file()
                                   )
        
        submenu_resolution = tk.Menu(self.menu_file, tearoff = False)
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
        
        self.menu_file.add_cascade(label = "Resolution", menu = submenu_resolution)
        self.menu_file.add_command(label = "Exit", underline = 0, command = lambda: self.close())
        
        file_button["menu"] = self.menu_file
        file_button.place(x = 0, y = 0)
        
        challenge_button = ttk.Menubutton(self.root, text = "Challenge")
        
        self.menu_challenge = tk.Menu(challenge_button, tearoff = False)
        self.menu_challenge.add_command(label = "Open",
                                        underline = 0,
                                        command = lambda: self.open_challenge_file()
                                        )
        
        self.menu_challenge.add_command(label = "Abort",
                                        underline = 0,
                                        state = "disabled"
                                        )
        
        self.menu_challenge.add_checkbutton(label = "Show time left",
                                            underline = 0,
                                            state = 'active',
                                            variable = self.show_time_left,
                                            onvalue = True,
                                            offvalue = False,
                                            command = self.toggle_time_display
                                            )
        
        challenge_button["menu"] = self.menu_challenge
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
        self.root.after(1000, self.check_queue)
        self.root.mainloop()
    
    def toggle_time_display(self):
        if self.show_time_left.get():
            label_x = {"normal": 300,
                              "high": 384,
                              "ultra": 600
                              }[self.size.get()]
            self.labels["timer"].place(x = label_x, y = 11, anchor = tk.E)
        else:
            self.labels["timer"].place_forget()
    
    def update_menu_states(self, in_challenge: bool):
        disabled = lambda on: "active" if not on else "disabled"
        self.menu_file.entryconfigure("Resolution", state = disabled(in_challenge))
        self.menu_file.entryconfigure("Open", state = disabled(in_challenge))
        self.menu_challenge.entryconfigure("Abort", state = disabled(not in_challenge))
        self.menu_challenge.entryconfigure("Open", state = disabled(in_challenge))
        self.menu_challenge.entryconfigure("Show time left", state = disabled(in_challenge))
    
    def update_time_display(self):
        if not self.show_time_left.get(): return
        
        if self.challenge == None:
            self.labels["timer"]["text"] = "0:00"
        
        elif self.challenge.mode == "marathon":
            self.labels["timer"]["text"] = "Marathon"
        
        else:
            remaining_time = int(self.challenge_end_time - time.time())
            remaining_seconds = remaining_time % 60
            remaining_minutes = remaining_time // 60
            
            if remaining_seconds >= 10:
                self.labels["timer"]["text"] = f"{remaining_minutes}:{remaining_seconds}"
            else:
                self.labels["timer"]["text"] = f"{remaining_minutes}:0{remaining_seconds}"