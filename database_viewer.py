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

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.characters_tab = ttk.Frame(self.tab_control)
        self.players_tab = ttk.Frame(self.tab_control)
        self.player_characters_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.characters_tab, text='Characters')
        self.tab_control.add(self.players_tab, text='Players')
        self.tab_control.add(self.player_characters_tab, text='Player-Characters')

        self.tab_control.pack(expand=1, fill='both')

        self.characters_tree = ttk.Treeview(self.characters_tab, columns=('ID', 'Name', 'HP', 'Attack', 'Defense', 'Speed', 'Luck', 'Magic', 'Level', 'Skill1', 'Skill2', 'Image Path', 'Personality', 'Available Points'), show='headings')
        for col in self.characters_tree['columns']:
            self.characters_tree.heading(col, text=col)
        self.characters_tree.pack(expand=True, fill='both')

        self.players_tree = ttk.Treeview(self.players_tab, columns=('ID', 'Username', 'Password', 'Profile Picture'), show='headings')
        for col in self.players_tree['columns']:
            self.players_tree.heading(col, text=col)
        self.players_tree.pack(expand=True, fill='both')

        self.player_characters_tree = ttk.Treeview(self.player_characters_tab, columns=('Player ID', 'Character ID'), show='headings')
        for col in self.player_characters_tree['columns']:
            self.player_characters_tree.heading(col, text=col)
        self.player_characters_tree.pack(expand=True, fill='both')

    def populate_characters_table(self):
        self.c.execute("SELECT * FROM characters")
        for row in self.c.fetchall():
            self.characters_tree.insert('', tk.END, values=row)

    def populate_players_table(self):
        self.c.execute("SELECT * FROM players")
        for row in self.c.fetchall():
            self.players_tree.insert('', tk.END, values=row)

    def populate_player_characters_table(self):
        self.c.execute("SELECT * FROM player_characters")
        for row in self.c.fetchall():
            self.player_characters_tree.insert('', tk.END, values=row)

root = tk.Tk()
app = DatabaseViewer(root)
root.mainloop()
