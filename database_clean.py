import sqlite3

def clean_up_duplicates():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    # Find duplicate characters for each player and remove them
    c.execute('''DELETE FROM player_characters
                 WHERE rowid NOT IN (SELECT MIN(rowid)
                                     FROM player_characters
                                     GROUP BY player_id, character_id)''')

    conn.commit()
    conn.close()

def clear_tables():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    c.execute('DELETE FROM player_characters')
    c.execute('DELETE FROM characters')
    c.execute('DELETE FROM players')
    conn.commit()
    conn.close()
import sqlite3

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    # Create players table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    profile_picture TEXT
                )''')

    # Create characters table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hp INTEGER,
                    attack INTEGER,
                    defense INTEGER,
                    speed INTEGER,
                    luck INTEGER,
                    magic INTEGER,
                    level INTEGER,
                    skill1 TEXT,
                    skill2 TEXT,
                    image_path TEXT,
                    personality TEXT,
                    available_points INTEGER DEFAULT 0
                )''')

    # Create player_characters table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS player_characters (
                    player_id INTEGER,
                    character_id INTEGER,
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )''')

    conn.commit()
    conn.close()

def insert_initial_players():
    players = [
        ("drew", "hello", None),
        ("drew123", "poop", "static\\DALL·E 2024-06-26 14.09.36 - Create a 64x64 bit pixel art mage character. The mage should have a blue robe, a tall pointed hat, holding a staff with a glowing crystal at the top, .png"),
        ("dang", "poop", "static\\DALL·E 2024-06-26 14.10.00 - Create a 64x64 bit pixel art knight character. The knight should have silver armor, a helmet with a plume, holding a sword and shield, and a determine.png"),
        ("Drewskie", "zoskov-nAgmum-fuggi4", "static\\IMG_2330.webp"),
        ("MotherUnceasing", "W4ri0!", "static\\IMG_6126.jpeg"),
        ("test", "test", "static\\IMG_2330.webp"),
        ("Drew1", "jedkod-Respoh-5rovca", "static\\IMG_2445.jpeg")
    ]

    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    for player in players:
        c.execute('INSERT INTO players (username, password, profile_picture) VALUES (?, ?, ?)', player)
    
    conn.commit()
    conn.close()

def insert_initial_characters():
    characters = [
        {
            "name": "Villager",
            "hp": 50,
            "attack": 5,
            "defense": 5,
            "speed": 5,
            "luck": 5,
            "magic": 0,
            "level": 1,
            "skill1": "Harvest",
            "skill2": "Craft",
            "image_path": "/static/villager.png",
            "personality": "Hardworking and friendly.",
            "available_points": 0
        },
        # Add other characters here...
    ]
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    for char in characters:
        c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, available_points)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["available_points"]))
    
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Insert one character for each player
    for player_id in range(1, 8):
        for char in characters:
            c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, available_points)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["available_points"]))
            
            character_id = c.lastrowid
            c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', (player_id, character_id))
    
    conn.commit()
    conn.close()

clear_tables()