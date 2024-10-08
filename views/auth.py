from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


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
            logging.debug(f"Starting signup process for username: {username}")

            conn = get_db_connection()
            c = conn.cursor()

            # Check if username is already taken
            logging.debug("Checking if the username exists.")
            c.execute('SELECT * FROM players WHERE username = ?', (username,))
            user_exists = c.fetchone()

            if user_exists:
                logging.debug(f"Username {username} already exists.")
                flash("Username already exists. Please choose another one.", "danger")
                return redirect(url_for('auth.signup'))

            # Save the profile picture
            profile_picture_path = os.path.join('static', profile_picture.filename)
            profile_picture.save(profile_picture_path)
            logging.debug(f"Profile picture saved at: {profile_picture_path}")

            # Insert new player into the database
            c.execute('INSERT INTO players (username, password, profile_picture) VALUES (?, ?, ?)',
                      (username, password, profile_picture_path))
            conn.commit()
            logging.debug(f"Player {username} inserted into the database.")

            # Log the user in automatically
            c.execute('SELECT * FROM players WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            session['user_id'] = user['id']
            logging.debug(f"User {username} logged in with user_id: {user['id']}")

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
                        "personality": "Hardworking and friendly.",
                        "personality_description": ("A blacksmith and village council member from a humble village by the river. "
                        "From a young age, fascinated by the forge and taught by their father. "
                        "Lost their mother to an epidemic at 12, instilling a deep sense of responsibility. "
                        "Took over the forge at 25, bringing prosperity to the village. "
                        "Elected to the village council, advocating for trade improvements and defense. "
                        "Dependable, wise, stoic, innovative, and guarded. "
                        "Strives to protect the village, honor their parents, and foster community growth. "
                        "Interests include metalwork artistry, storytelling, and herbal studies. "
                        "Notable traits are scarred hands, an iron amulet from their father, and a deep voice."),
                        "neutral_points": 0,
                        "positive_points": 0,
                        "negative_points": 0,
                        "name_asked": "no",
                        "sprite_sheet_path": "/static/images/sprites/villager_sprite.png",
                        "sprite_json_path": "/static/images/sprites/villager_sprite.json",
                        "sound_folder_path": "/static/sounds/villager",
                        "class": "Villager"

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
                        "personality_description": "Only says 'Woof'. Sometimes responds with actions a dog would do. These appear in asterisks. Likes bones and wagging tail. Will comfort you and give you a lick. Very good at conveying thoughts and ideas via facial expressions.",
                        "neutral_points": 0,
                        "positive_points": 0,
                        "negative_points": 0,
                        "name_asked": "no",
                        "sprite_sheet_path": "/static/images/sprites/dog_sprite.png",
                        "sprite_json_path": "/static/images/sprites/dog_sprite.json",
                        "sound_folder_path": "/static/sounds/dog",
                        "class":"Dog"
                }
            ]

            for char in initial_characters:
                logging.debug(f"Inserting character {char['name']} for player {username}")
                
                # Insert a new instance of each character for this player
                c.execute('''INSERT INTO characters (name, hp, attack, defense, speed, luck, magic, level, skill1, skill2, image_path, personality, personality_description, neutral_points, positive_points, negative_points, name_asked, sprite_sheet_path, sprite_json_path, sound_folder_path, class )
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (char["name"], char["hp"], char["attack"], char["defense"], char["speed"], char["luck"], char["magic"], char["level"], char["skill1"], char["skill2"], char["image_path"], char["personality"], char["personality_description"], char["neutral_points"], char["positive_points"], char["negative_points"], char["name_asked"], char["sprite_sheet_path"], char["sprite_json_path"], char["sound_folder_path"], char["class"]))
                
                # Get the newly created character's ID
                new_character_id = c.lastrowid

                # Assign this new character to the player
                c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', 
                          (user['id'], new_character_id))
                logging.debug(f"Character {char['name']} assigned to player {username}")

            conn.commit()
            logging.debug(f"Account created successfully for {username}")
            flash("Account created successfully! Welcome!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            logging.error(f"An error occurred during signup: {e}")
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
