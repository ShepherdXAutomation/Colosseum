from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import sqlite3
import os
from views.auth import auth_bp


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management


app.register_blueprint(auth_bp)
app.register_blueprint(characters_bp)

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
        # Check if the character already exists by name
        c.execute('SELECT * FROM characters WHERE name = ?', (char["name"],))
        result = c.fetchone()

        # If the character doesn't exist, insert it
        if result is None:
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


@app.route('/main_menu')
def main_menu():
    user = None
    if 'user_id' in session:
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
    return render_template('index.html', user=user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
