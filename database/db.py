import sqlite3

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    conn = get_db_connection()
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
                   available_points INTEGER DEFAULT 0,
                   personality_description TEXT,
                   neutral_points INTEGER DEFAULT 0,
                   positive_points INTEGER DEFAULT 0,
                   negative_points INTEGER DEFAULT 0
               )''')

    # Create player_characters table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS player_characters (
                    player_id INTEGER,
                    character_id INTEGER,
                    available_points INTEGER DEFAULT 0,
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )''')

    # Create memories table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    player_id INTEGER,
                    memory_log TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(character_id) REFERENCES characters(id),
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )''')

    conn.commit()
    conn.close()

# Save a new memory in the database
# Save memory in the format for future recall
def save_memory(character_id, player_id, memory_log):
    conn = get_db_connection()
    c = conn.cursor()

    # Check if the memory log is None or empty before saving
    if memory_log is None or memory_log == '':
        print(f"Warning: memory_log is empty for character_id {character_id} and player_id {player_id}.")
        memory_log = "No memory log provided."

    # Assuming memory_log is a simple string (you might need to adjust based on your use case)
    formatted_memory = memory_log  # If it's already a string, no need to format

    # Save memory to the database
    c.execute('INSERT INTO memories (character_id, player_id, memory_log) VALUES (?, ?, ?)',
              (character_id, player_id, formatted_memory))
    conn.commit()
    conn.close()



# Fetch all memories for a character
def get_memories(character_id, player_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT memory_log FROM memories WHERE character_id = ? AND player_id = ?', (character_id, player_id))
    # Fetch as list of dictionaries or just memory logs
    memories = [row['memory_log'] for row in c.fetchall()]
    conn.close()
    return memories


# Get the count of interactions between player and character
def get_chat_count(character_id, player_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM memories WHERE character_id = ? AND player_id = ?', (character_id, player_id))
    count = c.fetchone()[0]
    conn.close()
    return count

# Level up the character after certain interactions
def level_up_character(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    # Increment character's level and award available stat points
    c.execute('UPDATE characters SET level = level + 1, available_points = available_points + 1 WHERE id = ?', (character_id,))
    conn.commit()
    conn.close()



def get_character_by_id(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    
    conn.close()
    return character


def set_personality_description(character_id, description):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE characters SET personality_description = ? WHERE id = ?', (description, character_id))
    conn.commit()
    conn.close()


def get_personality_description(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT personality_description FROM characters WHERE id = ?', (character_id,))
    description = c.fetchone()
    conn.close()
    return description[0] if description else None




def column_exists(cursor, table_name, column_name):
    """
    Check if a specific column exists in a given table.
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Debugging: print all columns in the table
    print(f"Columns in '{table_name}': {columns}")
    
    return column_name in columns

def add_columns_if_not_exist():
    """
    Add necessary columns to the 'characters' table if they don't exist.
    This function only runs if at least one column is missing.
    """
    conn = get_db_connection()
    c = conn.cursor()

    # Columns to add and their types
    columns_to_add = [
        ('level', 'INTEGER'),
        ('skill1', 'TEXT'),
        ('skill2', 'TEXT'),
        ('personality', 'TEXT'),
        ('available_points', 'INTEGER DEFAULT 0'),
        ('personality_description', 'TEXT'),
        ('neutral_points', 'INTEGER DEFAULT 0'),
        ('positive_points', 'INTEGER DEFAULT 0'),
        ('negative_points', 'INTEGER DEFAULT 0'),
    ]

    # Check if any column is missing
    columns_exist = True
    for column, _ in columns_to_add:
        if not column_exists(c, 'characters', column):
            columns_exist = False
            break

    # If all columns exist, skip adding new columns
    if columns_exist:
        print("All required columns already exist. Skipping column addition.")
        conn.close()
        return

    # Otherwise, attempt to add missing columns
    for column, column_type in columns_to_add:
        if not column_exists(c, 'characters', column):
            try:
                c.execute(f'ALTER TABLE characters ADD COLUMN {column} {column_type}')
                print(f"Column '{column}' added successfully.")
            except sqlite3.OperationalError as e:
                print(f"Error adding column '{column}': {e}")
        else:
            print(f"Column '{column}' already exists.")

    conn.commit()
    conn.close()


# Insert initial characters into the database if they don't exist
# def insert_initial_characters():
#     characters = [
#         {
#             "name": "Villager",
#             "hp": 50,
#             "attack": 5,
#             "defense": 5,
#             "speed": 5,
#             "luck": 5,
#             "magic": 0,
#             "level": 1,
#             "skill1": "Harvest",
#             "skill2": "Craft",
#             "image_path": "/static/villager.png",
#             "personality": "Hardworking and friendly.",
#             "personality_description": "Loves beef stew. Hardworking and friendly. A person of very few words."
#         },
#         {
#             "name": "Friendly Dog",
#             "hp": 60,
#             "attack": 7,
#             "defense": 4,
#             "speed": 8,
#             "luck": 10,
#             "magic": 0,
#             "level": 1,
#             "skill1": "Fetch",
#             "skill2": "Bark",
#             "image_path": "/static/shaggy_brown_dog.png",
#             "personality": "Loyal and playful.",
#             "personality_description": "Only says 'Woof'. Likes bones and wagging tail. Will comfort you and give you a lick."
#         },
#         # Add more characters here if needed...
#     ]

#     conn = get_db_connection()
#     c = conn.cursor()

#     for char in characters:
#         # Check if the character already exists by name
#         c.execute('SELECT * FROM characters WHERE name = ?', (char["name"],))
#         result = c.fetchone()

#         # If the character doesn't exist, insert it
#         if result is None:
#             c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, personality_description)
#                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#                       (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["personality_description"], char["neutral_points"], char["positive_points"], char["negative_points"]))

#     conn.commit()
#     conn.close()

# Initialize the database and insert initial characters
init_db()
add_columns_if_not_exist()
# insert_initial_characters()
