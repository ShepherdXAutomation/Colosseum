from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

# Create the Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_picture = request.files['profile_picture']

        conn = None
        try:
            conn = get_db_connection()
            c = conn.cursor()

            # Check if username is already taken
            c.execute('SELECT * FROM players WHERE username = ?', (username,))
            user_exists = c.fetchone()

            if user_exists:
                flash("Username already exists. Please choose another one.", "danger")
                return redirect(url_for('auth.signup'))

            # Save the profile picture
            profile_picture_path = os.path.join('static', profile_picture.filename)
            profile_picture.save(profile_picture_path)

            # Insert new player into the database
            c.execute('INSERT INTO players (username, password, profile_picture) VALUES (?, ?, ?)',
                      (username, password, profile_picture_path))
            conn.commit()

            # Log the user in automatically
            c.execute('SELECT * FROM players WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            session['user_id'] = user['id']

            # Now create new instances of the initial characters for this player
            initial_characters = [
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
                    "personality": "Loyal and friendly."
                }
            ]

            for char in initial_characters:
                # Insert a new instance of each character for this player
                c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"]))
                
                # Get the newly created character's ID
                new_character_id = c.lastrowid

                # Assign this new character to the player
                c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', 
                          (user['id'], new_character_id))

            conn.commit()
            flash("Account created successfully! Welcome!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"An error occurred during signup: {e}", "danger")
            return redirect(url_for('auth.signup'))
        
        finally:
            if conn:
                conn.close()

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = None
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM players WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()

            if user:
                session['user_id'] = user['id']
                flash("Logged in successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials. Please try again.", "danger")
                return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"An error occurred during login: {e}", "danger")
            return redirect(url_for('auth.login'))
        
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have successfully logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/change_profile_picture', methods=['POST'])
def change_profile_picture():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    profile_picture = request.files['profile_picture']
    conn = None
    try:
        if profile_picture:
            profile_picture_path = os.path.join('static', profile_picture.filename)
            profile_picture.save(profile_picture_path)

            conn = get_db_connection()
            c = conn.cursor()
            c.execute('UPDATE players SET profile_picture = ? WHERE id = ?', 
                      (profile_picture_path, session['user_id']))
            conn.commit()

            flash("Profile picture updated successfully!", "success")
        else:
            flash("No profile picture selected.", "warning")

    except Exception as e:
        flash(f"An error occurred while updating your profile picture: {e}", "danger")
    
    finally:
        if conn:
            conn.close()

    return redirect(url_for('index'))
