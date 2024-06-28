from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

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

    try:
        c.execute('ALTER TABLE characters ADD COLUMN available_points INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print(f"Column 'available_points' already exists: {e}")

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
        {
            "name": "Friendly Dog",
            "hp": 30,
            "attack": 3,
            "defense": 2,
            "speed": 6,
            "luck": 8,
            "magic": 0,
            "level": 1,
            "skill1": "Bark",
            "skill2": "Fetch",
            "image_path": "/static/shaggy_brown_dog.png",
            "personality": "Loyal and friendly.",
            "available_points": 0
        }
    ]
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    for char in characters:
        c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, available_points)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["available_points"]))
    
    conn.commit()
    conn.close()

init_db()
add_columns_if_not_exist()
insert_initial_characters()

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
    return render_template('index.html', user=user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_picture = request.files['profile_picture']
        profile_picture_path = os.path.join('static', profile_picture.filename)
        profile_picture.save(profile_picture_path)
        
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('INSERT INTO players (username, password, profile_picture) VALUES (?, ?, ?)', 
                  (username, password, profile_picture_path))
        conn.commit()
        
        # Log in the user automatically
        c.execute('SELECT * FROM players WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        session['user_id'] = user[0]
        
        # Assign Villager and Friendly Dog character to the new player
        c.execute('SELECT id FROM characters WHERE name = "Villager"')
        villager_id = c.fetchone()[0]
        c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', (user[0], villager_id))
        
        c.execute('SELECT id FROM characters WHERE name = "Friendly Dog"')
        dog_id = c.fetchone()[0]
        c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', (user[0], dog_id))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/character_collection')
def character_collection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''SELECT characters.id, characters.name, characters.image_path
                 FROM characters
                 JOIN player_characters ON characters.id = player_characters.character_id
                 WHERE player_characters.player_id = ?''', (session['user_id'],))
    characters = c.fetchall()
    conn.close()
    
    return render_template('character_collection.html', characters=characters)

@app.route('/character_editor/<int:character_id>', methods=['GET', 'POST'])
def character_editor(character_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        # Update character stats
        hp = request.form['hp']
        attack = request.form['attack']
        defense = request.form['defense']
        speed = request.form['speed']
        luck = request.form['luck']
        magic = request.form['magic']
        available_points = request.form['available_points']
        
        c.execute('''UPDATE characters
                     SET hp = ?, attack = ?, defense = ?, speed = ?, luck = ?, magic = ?, available_points = ?
                     WHERE id = ?''',
                  (hp, attack, defense, speed, luck, magic, available_points, character_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('character_collection'))
    
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    conn.close()
    
    if character is None:
        return "Character not found", 404
    
    character_data = {
        "id": character[0],
        "name": character[1],
        "hp": character[2],
        "attack": character[3],
        "defense": character[4],
        "speed": character[5],
        "luck": character[6],
        "magic": character[7],
        "level": character[8],
        "skill1": character[9],
        "skill2": character[10],
        "image_path": character[11],
        "personality": character[12],
        "available_points": character[13],
    }
    
    return render_template('character_editor.html', character=character_data)


@app.route('/change_profile_picture', methods=['POST'])
def change_profile_picture():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    profile_picture = request.files['profile_picture']
    if profile_picture:
        profile_picture_path = os.path.join('static', profile_picture.filename)
        profile_picture.save(profile_picture_path)
        
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('UPDATE players SET profile_picture = ? WHERE id = ?', (profile_picture_path, session['user_id']))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/add_character_to_player/<int:character_id>', methods=['POST'])
def add_character_to_player(character_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Check if the character is already assigned to the player
    c.execute('''SELECT * FROM player_characters
                 WHERE player_id = ? AND character_id = ?''', (session['user_id'], character_id))
    character_exists = c.fetchone()
    
    if not character_exists:
        # Add character to the player's collection
        c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', (session['user_id'], character_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('character_collection'))


@app.route('/main_menu')
def main_menu():
    user = None
    if 'user_id' in session:
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
    return render_template('main_menu.html', user=user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
