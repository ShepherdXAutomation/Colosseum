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
                    image_path TEXT
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

def add_profile_picture_column():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE players ADD COLUMN profile_picture TEXT')
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    conn.commit()
    conn.close()

init_db()
add_profile_picture_column()

from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

@app.route('/player/<int:player_id>')
def player(player_id):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE id = ?', (player_id,))
    player = c.fetchone()
    
    c.execute('''SELECT characters.name, characters.hp, characters.attack, characters.defense, characters.speed, characters.luck, characters.magic, characters.image_path
                 FROM characters
                 JOIN player_characters ON characters.id = player_characters.character_id
                 WHERE player_characters.player_id = ?''', (player_id,))
    characters = c.fetchall()
    conn.close()
    
    return render_template('player.html', player=player, characters=characters)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
