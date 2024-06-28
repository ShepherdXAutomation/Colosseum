import sqlite3

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    # Drop tables if they exist to start fresh
    c.execute('DROP TABLE IF EXISTS player_characters')
    c.execute('DROP TABLE IF EXISTS characters')
    c.execute('DROP TABLE IF EXISTS players')

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

def debug_characters_table():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('PRAGMA table_info(characters)')
    columns = c.fetchall()
    print("Characters table columns:")
    for column in columns:
        print(column)
    conn.close()

init_db()
insert_initial_characters()
debug_characters_table()
