import sqlite3
import tkinter as tk
from tkinter import ttk

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Viewer")

        self.conn = sqlite3.connect('game.db')
        self.c = self.conn.cursor()

        self.create_widgets()
        self.populate_characters_table()
        self.populate_players_table()
        self.populate_player_characters_table()
        self.populate_memories_table()

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.characters_tab = ttk.Frame(self.tab_control)
        self.players_tab = ttk.Frame(self.tab_control)
        self.player_characters_tab = ttk.Frame(self.tab_control)
        self.memories_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.characters_tab, text='Characters')
        self.tab_control.add(self.players_tab, text='Players')
        self.tab_control.add(self.player_characters_tab, text='Player-Characters')
        self.tab_control.add(self.memories_tab, text='Memories')

        self.tab_control.pack(expand=1, fill='both')

        # Characters table with player username and personality_description columns
        self.characters_tree = ttk.Treeview(self.characters_tab, columns=('ID', 'Name', 'HP', 'Attack', 'Defense', 'Speed', 'Luck', 'Magic', 'Level', 'Skill1', 'Skill2', 'Image Path', 'Personality', 'Available Points', 'Personality Description', 'Positive Points', 'Neutral Points', 'Negative Points', 'Username'), show='headings')
        for col in self.characters_tree['columns']:
            self.characters_tree.heading(col, text=col)
        self.characters_tree.pack(expand=True, fill='both')

        # Players table
        self.players_tree = ttk.Treeview(self.players_tab, columns=('ID', 'Username', 'Password', 'Profile Picture'), show='headings')
        for col in self.players_tree['columns']:
            self.players_tree.heading(col, text=col)
        self.players_tree.pack(expand=True, fill='both')

        # Player-Characters table with username column
        self.player_characters_tree = ttk.Treeview(self.player_characters_tab, columns=('Player ID', 'Username', 'Character ID'), show='headings')
        for col in self.player_characters_tree['columns']:
            self.player_characters_tree.heading(col, text=col)
        self.player_characters_tree.pack(expand=True, fill='both')

        # Memories table with username column
        self.memories_tree = ttk.Treeview(self.memories_tab, columns=('ID', 'Character ID', 'Player ID', 'Username', 'Memory Log', 'Timestamp'), show='headings')
        for col in self.memories_tree['columns']:
            self.memories_tree.heading(col, text=col)
        self.memories_tree.pack(expand=True, fill='both')

    def populate_characters_table(self):
        # Join characters with player_characters and players to get the username and personality_description
        self.c.execute('''SELECT c.id, c.name, c.hp, c.attack, c.defense, c.speed, c.luck, c.magic, 
                                 c.level, c.skill1, c.skill2, c.image_path, c.personality, c.available_points, 
                                 c.personality_description, c.positive_points, c.neutral_points, c.negative_points, p.username
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
        # Join player_characters with players to get the username
        self.c.execute('''SELECT pc.player_id, p.username, pc.character_id 
                          FROM player_characters pc
                          JOIN players p ON pc.player_id = p.id''')
        for row in self.c.fetchall():
            self.player_characters_tree.insert('', tk.END, values=row)

    def populate_memories_table(self):
        # Join memories with players to get the username
        self.c.execute('''SELECT m.id, m.character_id, m.player_id, p.username, m.memory_log, m.timestamp
                          FROM memories m
                          JOIN players p ON m.player_id = p.id''')
        for row in self.c.fetchall():
            self.memories_tree.insert('', tk.END, values=row)

root = tk.Tk()
app = DatabaseViewer(root)
root.mainloop()
