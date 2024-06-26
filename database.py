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
                    personality TEXT
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

def add_columns_if_not_exist():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    try:
        c.execute('ALTER TABLE characters ADD COLUMN level INTEGER')
    except sqlite3.OperationalError as e:
        print(f"Column 'level' already exists: {e}")

    try:
        c.execute('ALTER TABLE characters ADD COLUMN skill1 TEXT')
    except sqlite3.OperationalError as e:
        print(f"Column 'skill1' already exists: {e}")

    try:
        c.execute('ALTER TABLE characters ADD COLUMN skill2 TEXT')
    except sqlite3.OperationalError as e:
        print(f"Column 'skill2' already exists: {e}")

    try:
        c.execute('ALTER TABLE characters ADD COLUMN personality TEXT')
    except sqlite3.OperationalError as e:
        print(f"Column 'personality' already exists: {e}")

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
            "personality": "Hardworking and friendly."
        },
        # Add other characters here...
    ]
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    for char in characters:
        c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"]))
    
    conn.commit()
    conn.close()

init_db()
add_columns_if_not_exist()
insert_initial_characters()
