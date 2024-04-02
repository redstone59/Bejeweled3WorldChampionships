from challenges import *

import tkinter as tk
from tkinter import ttk

from tkinter import messagebox, filedialog

ALL_SUBCHALLENGES = list(CHALLENGE_DATA.keys())
ALL_SUBCHALLENGES.sort()

def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return 0

class ChallengeCreator:
    def __init__(self):        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.is_timed_challenge = tk.BooleanVar()
        self.time_bonus_enabled = tk.BooleanVar()
        
        ttk.Button(text = "New", command = self.file_new).grid(column = 0, columnspan = 2, row = 0, padx = 5, pady = 5)
        ttk.Button(text = "Open", command = self.file_open).grid(column = 0, columnspan = 2, row = 1, padx = 5, pady = 5)
        ttk.Button(text = "Save", command = self.file_save).grid(column = 0, columnspan = 2, row = 2, padx = 5, pady = 5)
        ttk.Button(text = "Save as", command = self.file_save_as).grid(column = 0, columnspan = 2, row = 3, padx = 5, pady = 5)
        
        self.set_up_challenge_half()
        ttk.Separator(self.root, orient = "horizontal").grid(column = 0, row = 5, columnspan = 6, sticky = "ew", pady = 10)
        self.set_up_subchallenge_half()
        
        self.file_new()
    
    def add_new_subchallenge(self):
        self.subchallenge_tree.insert("", "end")
        last_id = self.subchallenge_tree.get_children()[-1]
        self.subchallenge_tree.selection_set(last_id)
    
    def change_challenge_mode(self):
        if self.is_timed_challenge.get():
            self.challenge_time_label.grid(column = 2, row = 4, pady = 5)
            self.challenge_time_box.grid(column = 3, row = 4)
        else:
            self.challenge_time_label.grid_forget()
            self.challenge_time_box.grid_forget()
        
        self.update_subchallenge_objective()
    
    def change_subchallenge(self, *args):
        self.save_subchallenge()
        tree_id = self.subchallenge_tree.selection()[0]

        if tree_id in self.id_subchallenge_dict:
            self.load_subchallenge(tree_id)
        else:
            self.new_subchallenge()
    
    def change_tree_item_names(self, *args):
        i = 1
        for child in self.subchallenge_tree.get_children():
            objective = self.id_subchallenge_dict[child].objective
            self.subchallenge_tree.set(child, '', f"{i}: {objective}")
            i += 1
    
    def file_new(self):
        for child in self.subchallenge_tree.get_children():
            self.subchallenge_tree.delete(child)
        
        self.root.title("BJ3WC Challenge Creator")
        self.file_changed_flag = False
        self.current_file = None
        self.previous_ids = [("I001",)] * 3
        self.id_subchallenge_dict = {}
        
        self.subchallenge_tree.insert("", "end", values = ["1: Classic"])
        self.subchallenge_tree.selection_set(self.subchallenge_tree.get_children()[0])
        self.new_subchallenge()
        
        self.title_box.delete(0, len(self.title_box.get()))
        self.author_box.delete(0, len(self.author_box.get()))
        self.description_box.delete(0, len(self.description_box.get()))
        self.is_timed_challenge.set(False)
        self.challenge_time_box.delete(0, len(self.challenge_time_box.get()))
    
    def file_open(self):
        challenge_file = filedialog.askopenfilename(parent = self.root, title = "Open challenge file", filetypes = [("JSON file", ".json")])
        
        try:
            with open(challenge_file) as file:
                challenge_to_load = load_challenge_json(file.read())
        
        except (InvalidChallengeError, InvalidSubchallengeError) as e:
            self.subchallenge_text["text"] = f"Invalid challenge!\n{e.__class__}: {e}"
            return
        
        for child in self.subchallenge_tree.get_children():
            self.subchallenge_tree.delete(child)
        
        self.title_box.delete(0, len(self.title_box.get()))
        self.author_box.delete(0, len(self.author_box.get()))
        self.description_box.delete(0, len(self.description_box.get()))
        self.is_timed_challenge.set(False)
        self.challenge_time_box.delete(0, len(self.challenge_time_box.get()))
        
        self.current_file = challenge_file
        self.root.title(f"BJ3WC Challenge Creator - {self.current_file}")
        
        self.title_box.insert(0, challenge_to_load.name)
        self.author_box.insert(0, challenge_to_load.author)
        self.description_box.insert(0, challenge_to_load.description)
        self.is_timed_challenge.set(challenge_to_load.mode == "timed")
        self.challenge_time_box.insert(0, str(challenge_to_load.time))
        
        self.change_challenge_mode()
        
        i = 1
        for subchallenge in challenge_to_load.subchallenges:
            i += 1
            self.subchallenge_tree.insert("", "end", values = ["***"])
            self.id_subchallenge_dict[f"I{str(i).zfill(3)}"] = subchallenge
        
        self.change_tree_item_names()
    
    def file_save(self):
        title = self.title_box.get()
        author = self.author_box.get()
        description = self.description_box.get()
        if self.is_timed_challenge.get():
            mode = "timed"
            time = safe_int(self.challenge_time_box.get())
        else:
            mode = "marathon"
            time = None
            
        subchallenges = [subchallenge for subchallenge in self.id_subchallenge_dict.values()]
        
        if self.current_file == None:
            file_types = (("JSON File", "*.json"), ("All Files", "*.*"))
            file_name = f"{title}.json" if title != "" else "My Bejeweled 3 Challenge.json"
            self.current_file = filedialog.asksaveasfilename(title = "Pick a save location",
                                                             initialdir = "./",
                                                             filetypes = file_types,
                                                             initialfile = file_name
                                                             )
        
        with open(self.current_file, "w") as file:
            challenge = Challenge(title, author, description, mode, subchallenges, time)
            file.write(json.dumps(challenge.to_dict(), indent = 4))
            print(challenge.to_dict())
        
        self.root.title(f"BJ3WC Challenge Creator - {self.current_file}")
        self.subchallenge_text["text"] = f"Saved file at {self.current_file}"
        self.file_changed_flag = False
    
    def file_save_as(self):
        self.current_file = None
        self.file_save()
    
    def get_previous_id(self):
        return self.previous_ids[-2]
    
    def load_subchallenge(self, tree_id: str):
        subchallenge: Subchallenge = self.id_subchallenge_dict[tree_id]
        self.objective_selector.set(subchallenge.objective)
        self.mode_selector.set(subchallenge.mode.capitalize())
        self.multiplier_box.set(str(subchallenge.multiplier))
        
        self.condition_box.delete(0, len(self.condition_box.get()))
        if subchallenge.mode == "value":
            self.condition_box.insert(0, str(subchallenge.condition))
        
        self.time_box.delete(0, len(self.time_box.get()))
        self.time_bonus_enabled.set(False)
        if subchallenge.mode == "timed" or subchallenge.time_bonus_enabled:
            self.time_box.insert(0, str(subchallenge.time))
            self.time_bonus_enabled.set(subchallenge.time_bonus_enabled)
        
        self.poker_hand_box.delete(0, len(self.poker_hand_box.get()))
        if subchallenge.objective == "PokerHand":
            self.poker_hand_box.set(subchallenge.extra)
        elif subchallenge.extra != None:
            self.extra_box.set(subchallenge.extra)
        else:
            self.extra_box.set(1)
        
        self.update_subchallenge_objective()
        self.update_subchallenge_mode()
    
    def new_subchallenge(self):
        self.objective_selector.set("Classic")
        self.mode_selector.set("Value")
        self.multiplier_box.set(1)
        self.condition_box.delete(0, len(self.condition_box.get()))
        self.time_box.delete(0, len(self.time_box.get()))
        self.extra_box.set(1)
        self.poker_hand_box.delete(0, len(self.poker_hand_box.get()))
        self.update_subchallenge_objective()
        self.update_subchallenge_mode()
    
    def on_close(self):
        if self.file_changed_flag:
            if not messagebox.askyesno("Unsaved changes", "Are you sure you want to exit without saving?"):
                return
            
        self.root.destroy()
    
    def remove_selected_subchallenge(self):
        if len(self.subchallenge_tree.get_children()) == 1: return
        
        self.subchallenge_tree.delete(self.subchallenge_tree.selection())
        first_id = self.subchallenge_tree.get_children()[0]
        self.subchallenge_tree.selection_set(first_id)
        self.change_tree_item_names()
    
    def save_subchallenge(self, *args):
        tree_selection = self.update_previous_id()
        
        if tree_selection == ():
            return
        
        self.file_changed_flag = True
        
        tree_selection = tree_selection[0]
        
        objective = self.objective_selector.get()
        mode = self.mode_selector.get().lower()
        multiplier = safe_int(self.multiplier_box.get())
        
        optional_args = {}
        
        if mode == "value":
            optional_args["condition"] = safe_int(self.condition_box.get())
            if self.time_bonus_enabled.get():
                optional_args["time_bonus_enabled"] = True
                optional_args["time"] = safe_int(self.time_box.get())
        elif mode == "timed":
            optional_args["time"] = safe_int(self.time_box.get())
        
        quests_with_extras = ["Avalanche", "Balance", "Butterflies", "ButterClear", "ButterCombo", "TimeBomb", "MatchBomb", "PokerHand"]
        if objective in quests_with_extras:
            if objective == "PokerHand":
                optional_args["extra"] = self.poker_hand_box.get()
            else:
                optional_args["extra"] = safe_int(self.extra_box.get())
        
        self.id_subchallenge_dict[tree_selection] = Subchallenge(objective, mode, multiplier, **optional_args)
        self.update_subchallenge_text(tree_selection)
    
    def set_up_challenge_half(self):
        tk.Label(text = "Name: ").grid(column = 2, row = 0)
        self.title_box = ttk.Entry(self.root,
                                   width = 45
                                   )
        self.title_box.grid(column = 3, row = 0)
        
        tk.Label(text = "Author: ").grid(column = 2, row = 1)
        self.author_box = ttk.Entry(self.root,
                                    width = 45
                                    )
        self.author_box.grid(column = 3, row = 1)
        
        tk.Label(text = "Description: ").grid(column = 2, row = 2)
        self.description_box = ttk.Entry(self.root,
                                         width = 45
                                         )
        self.description_box.grid(column = 3, row = 2)
        
        tk.Label(text = "Timed challenge?: ").grid(column = 2, row = 3)
        self.timed_box = ttk.Checkbutton(self.root,
                                         variable = self.is_timed_challenge,
                                         onvalue = True,
                                         offvalue = False,
                                         command = self.change_challenge_mode
                                         )
        self.timed_box.grid(column = 3, row = 3)
        
        self.challenge_time_label = tk.Label(text = "Time: ")
        self.challenge_time_box = ttk.Spinbox(self.root, from_ = 1, to = 2 ** 31)
    
    def set_up_subchallenge_half(self):
        self.subchallenge_tree = ttk.Treeview(self.root, selectmode = "browse", columns = [""], show = "")
        self.subchallenge_tree.bind("<<TreeviewSelect>>", self.change_subchallenge)
        self.subchallenge_tree.grid(column = 0, columnspan = 2, row = 6, rowspan = 7)
        self.subchallenge_tree.column("#0", width = 120)
        
        ttk.Button(text = "Add", command = self.add_new_subchallenge).grid(column = 0, row = 13)
        ttk.Button(text = "Remove", command = self.remove_selected_subchallenge).grid(column = 1, row = 13)
        
        ttk.Label(text = "Objective: ").grid(column = 2, row = 6)
        self.objective_selector = ttk.Combobox(self.root)
        self.objective_selector["values"] = ALL_SUBCHALLENGES
        self.objective_selector.bind("<<ComboboxSelected>>", self.update_subchallenge_objective)
        self.objective_selector.grid(column = 3, row = 6)
        
        ttk.Label(text = "Type: ").grid(column = 2, row = 7)
        self.mode_selector = ttk.Combobox(self.root, state = "readonly")
        self.mode_selector["values"] = ["Value", "Timed"]
        self.mode_selector.bind("<<ComboboxSelected>>", self.update_subchallenge_mode)
        self.mode_selector.grid(column = 3, row = 7)
        
        self.condition_label = ttk.Label(text = "Condition: ")
        self.condition_box = ttk.Entry(self.root)
        self.condition_box.bind("<KeyRelease>", self.save_subchallenge)
        
        self.time_bonus_label = ttk.Label(text = "Score with time?")
        self.time_bonus_button = ttk.Checkbutton(self.root,
                                                 variable = self.time_bonus_enabled,
                                                 onvalue = True,
                                                 offvalue = False,
                                                 command = self.update_time_bonus
                                                 )
        
        self.time_label = ttk.Label(text = "Time: ")
        self.time_box = ttk.Spinbox(self.root, from_ = 1, to = 2 ** 31)
        self.time_box.bind("<KeyRelease>", self.save_subchallenge)
        
        self.extra_label = ttk.Label()
        self.extra_box = ttk.Spinbox(self.root, from_ = 1, to = 2 ** 31)
        self.extra_box.bind("<KeyRelease>", self.save_subchallenge)
        self.poker_hand_box = ttk.Combobox(self.root, state = "readonly")
        self.poker_hand_box.bind("<<ComboboxSelected>>", self.save_subchallenge)
        self.poker_hand_box["values"] = ["Pair", "Spectrum", "2 Pair", "3 of a Kind", "Full House", "4 of a Kind", "Flush"]
        
        ttk.Label(text = "Multiplier").grid(column = 2, row = 12, pady = 2)
        self.multiplier_box = ttk.Spinbox(self.root, from_ = 1, to = 999)
        self.multiplier_box.bind("<KeyRelease>", self.save_subchallenge)
        self.multiplier_box.grid(column = 3, row = 12)
        
        self.subchallenge_text = ttk.Label(text = "Subchallenge text will appear here.")
        self.subchallenge_text.grid(column = 0, row = 15, columnspan = 6, pady = 5)

    def start(self):
        self.root.mainloop()
    
    def update_previous_id(self):
        self.previous_ids += [self.subchallenge_tree.selection()]
        self.previous_ids = self.previous_ids[-3:]
        return self.previous_ids[-2]
    
    def update_subchallenge_mode(self, *args):
        widgets_to_remove: list[ttk.Widget] = [self.condition_box, self.condition_label,
                                               self.time_bonus_button, self.time_bonus_label,
                                               self.time_box, self.time_label]
        for x in widgets_to_remove:
            x.grid_forget()
        
        match self.mode_selector.get():
            case "Timed":
                self.time_label.grid(column = 2, row = 10, pady = 2)
                self.time_box.grid(column = 3, row = 10)
                self.time_bonus_enabled.set(False)
            case "Value":
                self.condition_label.grid(column = 2, row = 8)
                self.condition_box.grid(column = 3, row = 8)
                self.time_bonus_label.grid(column = 2, row = 9)
                self.time_bonus_button.grid(column = 3, row = 9)
                self.update_time_bonus()
        
        self.save_subchallenge()
    
    def update_subchallenge_objective(self, *args):
        self.extra_label.grid_forget()
        self.extra_box.grid_forget()
        self.poker_hand_box.grid_forget()
        
        allowed_modes: list[str] = CHALLENGE_DATA[self.objective_selector.get()]["allowed_modes"]
        allowed_modes = [x.capitalize() for x in allowed_modes]
        
        if not self.is_timed_challenge.get() and "Endless" in allowed_modes:
            allowed_modes.remove("Endless")
        
        self.mode_selector["values"] = allowed_modes
        
        quests_with_extras = ["Avalanche", "Balance", "Butterflies", "ButterClear", "ButterCombo", "TimeBomb", "MatchBomb", "PokerHand"]
        if self.objective_selector.get() not in quests_with_extras:
            self.save_subchallenge()
            self.change_tree_item_names()
            return
        
        self.extra_label.grid(column = 2, row = 11)
        self.extra_box.grid(column = 3, row = 11)
        
        match self.objective_selector.get():
            case "Avalanche":
                self.extra_label["text"] = "# gems/move: "
                self.extra_box.set(5)
            case "Balance":
                self.extra_label["text"] = "Gem scale speed: "
                self.extra_box.set(9)
            case "Butterflies" | "ButterClear" | "ButterCombo":
                self.extra_label["text"] = "# matches until butterflies move: "
                self.extra_box.set(1)
            case "TimeBomb" | "MatchBomb":
                self.extra_label["text"] = "Initial bomb #: "
                self.extra_box.set(30)
            case "PokerHand":
                self.extra_label["text"] = "Poker Hand: "
                self.extra_box.grid_forget()
                self.poker_hand_box.grid(column = 3, row = 11)
        
        self.save_subchallenge()
        self.change_tree_item_names()
                
    def update_subchallenge_text(self, id: str):
        self.subchallenge_text["text"] = str(self.id_subchallenge_dict[id])
    
    def update_time_bonus(self):
        if self.time_bonus_enabled.get():
            self.time_label.grid(column = 2, row = 10)
            self.time_box.grid(column = 3, row = 10)
        else:
            self.time_label.grid_forget()
            self.time_box.grid_forget()
        self.save_subchallenge()
        
creator = ChallengeCreator()
creator.start()
