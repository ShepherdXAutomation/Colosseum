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

            # Assign default characters (Villager and Friendly Dog)
            c.execute('SELECT id FROM characters WHERE name = "Villager"')
            villager_id = c.fetchone()['id']
            c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', 
                      (user['id'], villager_id))

            c.execute('SELECT id FROM characters WHERE name = "Friendly Dog"')
            dog_id = c.fetchone()['id']
            c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', 
                      (user['id'], dog_id))

            conn.commit()
            flash("Account created successfully! Welcome!", "success")
            return redirect(url_for('main_menu'))

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
                return redirect(url_for('main_menu'))
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

    return redirect(url_for('main_menu'))
