from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Create players table
    c.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    profile_picture TEXT
                )''')
    
    # Create characters table
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
    
    # Create player_characters table
    c.execute('''CREATE TABLE IF NOT EXISTS player_characters (
                    player_id INTEGER,
                    character_id INTEGER,
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )''')
    
    # Add columns if they do not exist
    try:
        c.execute('ALTER TABLE characters ADD COLUMN level INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute('ALTER TABLE characters ADD COLUMN skill1 TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute('ALTER TABLE characters ADD COLUMN skill2 TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

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
        
        # Assign Villager character to the new player
        c.execute('SELECT id FROM characters WHERE name = "Villager"')
        villager_id = c.fetchone()[0]
        c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', (user[0], villager_id))
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
        level = request.form['level']
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        
        c.execute('''UPDATE characters
                     SET hp = ?, attack = ?, defense = ?, speed = ?, luck = ?, magic = ?, level = ?, skill1 = ?, skill2 = ?
                     WHERE id = ?''',
                  (hp, attack, defense, speed, luck, magic, level, skill1, skill2, character_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('character_collection'))
    
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    conn.close()
    
    return render_template('character_editor.html', character=character)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
