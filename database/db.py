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
                    summarized INTEGER DEFAULT 0,
                    FOREIGN KEY(character_id) REFERENCES characters(id),
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )''')

    conn.commit()
    conn.close()





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
        ('name_asked', 'TEXT DEFAULT no')
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
            "personality_description": "Hardworking and friendly. A person of very few words.",
            "neutral_points": 0,
            "positive_points": 0,
            "negative_points": 0,
            "name_asked": "no"
        },
        {
            "name": "Friendly Dog",
            "hp": 60,
            "attack": 7,
            "defense": 4,
            "speed": 8,
            "luck": 10,
            "magic": 0,
            "level": 1,
            "skill1": "Fetch",
            "skill2": "Bark",
            "image_path": "/static/shaggy_brown_dog.png",
            "personality": "Loyal and playful.",
            "personality_description": "Only says 'Woof'. Sometimes responds with actions a dog would do. These appear in asterisks. Likes bones and wagging tail. Will comfort you and give you a lick.",
            "neutral_points": 0,
            "positive_points": 0,
            "negative_points": 0,
            "name_asked": "no"
        },
        # Add more characters here if needed...
    ]

    conn = get_db_connection()
    c = conn.cursor()

    for char in characters:
        # Check if the character already exists by name
        c.execute('SELECT * FROM characters WHERE name = ?', (char["name"],))
        result = c.fetchone()

        # If the character doesn't exist, insert it
        if result is None:
            c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, personality_description, neutral_points, positive_points, negative_points, name_asked)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
          (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["personality_description"], char["neutral_points"], char["positive_points"], char["negative_points"], char["name_asked"]))


    conn.commit()
    conn.close()

def update_disposition_points(character_id, tone):
    conn = get_db_connection()
    c = conn.cursor()

    if tone == 'positive':
        c.execute('UPDATE characters SET positive_points = positive_points + 1 WHERE id = ?', (character_id,))
    elif tone == 'negative':
        c.execute('UPDATE characters SET negative_points = negative_points + 1 WHERE id = ?', (character_id,))
    else:
        c.execute('UPDATE characters SET neutral_points = neutral_points + 1 WHERE id = ?', (character_id,))

    conn.commit()
    conn.close()
    print(f"Updated disposition points for character {character_id}: {tone} tone")


# Initialize the database and insert initial characters
init_db()
add_columns_if_not_exist()
insert_initial_characters()


#----------------Leveling System-------------------------------------

level_thresholds = {
    1: 10,    # 10 memories needed to reach level 2
    2: 25,    # 25 total memories to reach level 3
    3: 45,    # 45 total memories to reach level 4
    4: 70,    # 70 total memories to reach level 5
    5: 100,   # 100 total memories to reach level 6
    6: 135,   # 135 total memories to reach level 7
    7: 175,   # 175 total memories to reach level 8
    8: 220,   # 220 total memories to reach level 9
    9: 270,   # 270 total memories to reach level 10
   10: 325,   # 325 total memories to reach level 11
   11: 385,   # 385 total memories to reach level 12
   12: 450,   # 450 total memories to reach level 13
   13: 520,   # 520 total memories to reach level 14
   14: 595,   # 595 total memories to reach level 15
}
# Function to get the current level of a character
def get_current_level(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
    level = c.fetchone()['level']
    conn.close()
    return level

# Function to get the memory count for a character
def get_memory_count(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as memory_count FROM memories WHERE character_id = ?", (character_id,))
    memory_count = c.fetchone()['memory_count']
    conn.close()
    return memory_count

# Function to check if character needs to level up
def check_and_level_up(character_id):
    memory_count = get_memory_count(character_id)  # Fetch how many memories are stored
    current_level = get_current_level(character_id)
    
    if memory_count >= level_thresholds.get(current_level, float('inf')):
        level_up(character_id)  # Increment level
        print(f"Character {character_id} leveled up to {current_level + 1}")

# Function to level up the character and assign points
def level_up(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Increment level and reward points
    c.execute('UPDATE characters SET level = level + 1, available_points = available_points + 2 WHERE id = ?', (character_id,))
    conn.commit()
    conn.close()


def update_name_asked(character_id, name_asked='yes'):
    """
    Update the 'name_asked' column for a specific character.

    :param character_id: The ID of the character to update.
    :param name_asked: The value to set for 'name_asked', default is 'yes'.
    """
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('game.db')
        c = conn.cursor()

        # Update the 'name_asked' field for the character
        c.execute('UPDATE characters SET name_asked = ? WHERE id = ?', (name_asked, character_id))

        # Commit the changes
        conn.commit()
        print(f"Character {character_id} 'name_asked' updated to {name_asked}")

    except Exception as e:
        print(f"An error occurred while updating name_asked for character {character_id}: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def alter_table_add_column():
    conn = sqlite3.connect('game.db')  # Connect to your database
    c = conn.cursor()

    try:
        # Execute the ALTER TABLE statement to add a new column
        c.execute("ALTER TABLE memories ADD COLUMN summarized INTEGER DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        print("Column 'summarized' added successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        conn.close()


