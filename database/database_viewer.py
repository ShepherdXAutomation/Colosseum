import sqlite3
import tkinter as tk
from tkinter import ttk
import subprocess

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Viewer")
        self.root.geometry("1000x600")  # Set window size

        self.conn = sqlite3.connect('game.db')
        self.c = self.conn.cursor()

        self.create_widgets()
        self.populate_all_tables()
    def open_sql_executor(self):
        subprocess.Popen(['python', 'database\\sql_execute.py'])
    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.characters_tab = ttk.Frame(self.tab_control)
        self.players_tab = ttk.Frame(self.tab_control)
        self.player_characters_tab = ttk.Frame(self.tab_control)
        self.memories_tab = ttk.Frame(self.tab_control)
        self.disposition_tab = ttk.Frame(self.tab_control)
        self.weapons_tab = ttk.Frame(self.tab_control)  # New weapons tab

        self.tab_control.add(self.characters_tab, text='Characters')
        self.tab_control.add(self.players_tab, text='Players')
        self.tab_control.add(self.player_characters_tab, text='Player-Characters')
        self.tab_control.add(self.memories_tab, text='Memories')
        self.tab_control.add(self.disposition_tab, text='Disposition')
        self.tab_control.add(self.weapons_tab, text='Weapons')  # Add weapons tab

        self.tab_control.pack(expand=1, fill='both')
       


        # Create an Update button
        update_button = tk.Button(self.root, text="Update", command=self.update_tables)
        update_button.pack()
         # Add button to open the SQL Executor App
        sql_executor_button = tk.Button(self.root, text="Open SQL Executor", command=self.open_sql_executor)
        sql_executor_button.pack(pady=5)
        # Characters table (added 'Name Asked' column)
        self.characters_tree = ttk.Treeview(self.characters_tab, columns=('ID', 'Name', 'HP', 'Attack', 'Defense', 'Speed', 'Luck', 'Magic', 'Level', 'Skill1', 'Skill2', 'Image Path', 'Personality', 'Available Points', 'Personality Description', 'Positive Points', 'Neutral Points', 'Negative Points', 'Username', 'Name Asked'), show='headings')
        for col in self.characters_tree['columns']:
            self.characters_tree.heading(col, text=col)
        self.characters_tree.pack(expand=True, fill='both')

        # Players table
        self.players_tree = ttk.Treeview(self.players_tab, columns=('ID', 'Username', 'Password', 'Profile Picture'), show='headings')
        for col in self.players_tree['columns']:
            self.players_tree.heading(col, text=col)
        self.players_tree.pack(expand=True, fill='both')

        # Player-Characters table
        self.player_characters_tree = ttk.Treeview(self.player_characters_tab, columns=('Player ID', 'Username', 'Character ID'), show='headings')
        for col in self.player_characters_tree['columns']:
            self.player_characters_tree.heading(col, text=col)
        self.player_characters_tree.pack(expand=True, fill='both')

        # Memories table (with Character Name)
        self.memories_tree = ttk.Treeview(self.memories_tab, columns=('ID', 'Character Name', 'Character ID', 'Player ID', 'Username', 'Memory Log', 'Timestamp'), show='headings')
        for col in self.memories_tree['columns']:
            self.memories_tree.heading(col, text=col)
        self.memories_tree.pack(expand=True, fill='both')

        # Disposition table
        self.disposition_tree = ttk.Treeview(self.disposition_tab, columns=('Player Username', 'Character Name', 'Level', 'Positive Points', 'Neutral Points', 'Negative Points'), show='headings')
        for col in self.disposition_tree['columns']:
            self.disposition_tree.heading(col, text=col)
        self.disposition_tree.pack(expand=True, fill='both')

        # Weapons table (with Character Name) - NEW SECTION
        self.weapons_tree = ttk.Treeview(self.weapons_tab, columns=('Weapon ID', 'Weapon Name', 'Type', 'Attack Bonus', 'Defense Bonus', 'Magic Bonus', 'Speed Bonus', 'Owner Name'), show='headings')
        for col in self.weapons_tree['columns']:
            self.weapons_tree.heading(col, text=col)
        self.weapons_tree.pack(expand=True, fill='both')

        # Add scrollbars after creating the treeviews
        self.add_scrollbars()

    def add_scrollbars(self):
        """ Add horizontal scrollbars for each Treeview """
        self.scrollbar_x_chars = ttk.Scrollbar(self.characters_tab, orient='horizontal', command=self.characters_tree.xview)
        self.scrollbar_x_chars.pack(side=tk.BOTTOM, fill=tk.X)
        self.characters_tree.configure(xscrollcommand=self.scrollbar_x_chars.set)

        self.scrollbar_x_players = ttk.Scrollbar(self.players_tab, orient='horizontal', command=self.players_tree.xview)
        self.scrollbar_x_players.pack(side=tk.BOTTOM, fill=tk.X)
        self.players_tree.configure(xscrollcommand=self.scrollbar_x_players.set)

        self.scrollbar_x_pc = ttk.Scrollbar(self.player_characters_tab, orient='horizontal', command=self.player_characters_tree.xview)
        self.scrollbar_x_pc.pack(side=tk.BOTTOM, fill=tk.X)
        self.player_characters_tree.configure(xscrollcommand=self.scrollbar_x_pc.set)

        self.scrollbar_x_memories = ttk.Scrollbar(self.memories_tab, orient='horizontal', command=self.memories_tree.xview)
        self.scrollbar_x_memories.pack(side=tk.BOTTOM, fill=tk.X)
        self.memories_tree.configure(xscrollcommand=self.scrollbar_x_memories.set)

        self.scrollbar_x_disp = ttk.Scrollbar(self.disposition_tab, orient='horizontal', command=self.disposition_tree.xview)
        self.scrollbar_x_disp.pack(side=tk.BOTTOM, fill=tk.X)
        self.disposition_tree.configure(xscrollcommand=self.scrollbar_x_disp.set)

        self.scrollbar_x_weapons = ttk.Scrollbar(self.weapons_tab, orient='horizontal', command=self.weapons_tree.xview)
        self.scrollbar_x_weapons.pack(side=tk.BOTTOM, fill=tk.X)
        self.weapons_tree.configure(xscrollcommand=self.scrollbar_x_weapons.set)

    def populate_all_tables(self):
        self.populate_characters_table()
        self.populate_players_table()
        self.populate_player_characters_table()
        self.populate_memories_table()
        self.populate_disposition_table()
        self.populate_weapons_table()  # New function to populate weapons

    def clear_tables(self):
        """ Clear all tables before repopulating """
        for tree in [self.characters_tree, self.players_tree, self.player_characters_tree, self.memories_tree, self.disposition_tree, self.weapons_tree]:
            for item in tree.get_children():
                tree.delete(item)

    def update_tables(self):
        """ Clear and repopulate all tables when the Update button is clicked """
        self.clear_tables()
        self.populate_all_tables()

    def populate_characters_table(self):
        self.c.execute('''SELECT c.id, c.name, c.hp, c.attack, c.defense, c.speed, c.luck, c.magic, 
                                 c.level, c.skill1, c.skill2, c.image_path, c.personality, c.available_points, 
                                 c.personality_description, c.positive_points, c.neutral_points, c.negative_points, p.username, c.name_asked
                          FROM characters c
                          LEFT JOIN player_characters pc ON c.id = pc.character_id
                          LEFT JOIN players p ON pc.player_id = p.id''')
        for row in self.c.fetchall():
            self.characters_tree.insert('', tk.END, values=row)

    def populate_players_table(self):
        self.c.execute("SELECT * FROM players")
        for row in self.c.fetchall():
            self.players_tree.insert('', tk.END, values=row)

    def populate_player_characters_table(self):
        self.c.execute('''SELECT pc.player_id, p.username, pc.character_id 
                          FROM player_characters pc
                          JOIN players p ON pc.player_id = p.id''')
        for row in self.c.fetchall():
            self.player_characters_tree.insert('', tk.END, values=row)

    def populate_memories_table(self):
        self.c.execute('''SELECT m.id, c.name, m.character_id, m.player_id, p.username, m.memory_log, m.timestamp
                          FROM memories m
                          JOIN characters c ON m.character_id = c.id
                          JOIN players p ON m.player_id = p.id''')
        for row in self.c.fetchall():
            self.memories_tree.insert('', tk.END, values=row)

    def populate_disposition_table(self):
        self.c.execute('''SELECT p.username, c.name, c.level, c.positive_points, c.neutral_points, c.negative_points
                          FROM characters c
                          LEFT JOIN player_characters pc ON c.id = pc.character_id
                          LEFT JOIN players p ON pc.player_id = p.id''')
        for row in self.c.fetchall():
            self.disposition_tree.insert('', tk.END, values=row)

    def populate_weapons_table(self):  # New function to populate the weapons table
        self.c.execute('''SELECT w.id, w.name, w.type, w.attack_bonus, w.defense_bonus, w.magic_bonus, w.speed_bonus, c.name
                          FROM weapons w
                          LEFT JOIN characters c ON c.weapon_id = w.id''')
        for row in self.c.fetchall():
            self.weapons_tree.insert('', tk.END, values=row)


root = tk.Tk()
app = DatabaseViewer(root)
root.mainloop()