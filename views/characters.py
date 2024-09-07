# Manages character creation, editing, and display.
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import check_and_level_up, get_character_by_id, get_memories, save_memory, get_chat_count, level_up_character

import sqlite3

from utils.api import send_chatgpt_api

# Create the Blueprint for character routes
characters_bp = Blueprint('characters', __name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@characters_bp.route('/add_character_to_player/<int:character_id>', methods=['POST'])
def add_character_to_player(character_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Correct blueprint reference for 'login'
    
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if the character is already assigned to the player
        c.execute('''SELECT * FROM player_characters
                     WHERE player_id = ? AND character_id = ?''', (session['user_id'], character_id))
        character_exists = c.fetchone()
        
        if not character_exists:
            # Add character to the player's collection
            c.execute('INSERT INTO player_characters (player_id, character_id) VALUES (?, ?)', 
                      (session['user_id'], character_id))
            conn.commit()
            flash("Character added to your collection!", "success")
        else:
            flash("Character already exists in your collection.", "info")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('characters.character_collection'))  # Correct blueprint reference

@characters_bp.route('/character_editor/<int:character_id>', methods=['GET', 'POST'])
def character_editor(character_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = None
    try:
        conn = get_db_connection()
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
            flash("Character stats updated successfully!", "success")
            return redirect(url_for('characters.character_collection'))
        
        # Fetch character data for the editor
        c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        character = c.fetchone()
        
        if character is None:
            return "Character not found", 404
        
        character_data = {
            "id": character['id'],
            "name": character['name'],
            "hp": character['hp'],
            "attack": character['attack'],
            "defense": character['defense'],
            "speed": character['speed'],
            "luck": character['luck'],
            "magic": character['magic'],
            "level": character['level'],
            "skill1": character['skill1'],
            "skill2": character['skill2'],
            "image_path": character['image_path'],
            "personality": character['personality'],
            "available_points": character['available_points'],
        }
        return render_template('character_editor.html', character=character_data)
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('characters.character_collection'))
    finally:
        if conn:
            conn.close()

@characters_bp.route('/character_collection')
def character_collection():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Correct blueprint reference
    
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT characters.id, characters.name, characters.image_path
                     FROM characters
                     JOIN player_characters ON characters.id = player_characters.character_id
                     WHERE player_characters.player_id = ?''', (session['user_id'],))
        characters = c.fetchall()
        return render_template('character_collection.html', characters=characters)
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('characters.character_collection'))
    finally:
        if conn:
            conn.close()
@characters_bp.route('/tavern_select', methods=['GET'])
def tavern_select():
    player_id = session.get('user_id')
    if not player_id:
        return redirect(url_for('auth.login'))  # Redirect to login if user is not logged in

    conn = get_db_connection()
    c = conn.cursor()
    
    # Fetch all characters belonging to the current player
    c.execute('''SELECT characters.id, characters.name, characters.image_path 
                 FROM characters 
                 JOIN player_characters ON characters.id = player_characters.character_id 
                 WHERE player_characters.player_id = ?''', (player_id,))
    characters = c.fetchall()
    conn.close()
    
    return render_template('tavern_select.html', characters=characters)




# Existing functions and routes...
# (Keep all your existing functions and routes as they are)

# Add this new function to handle Socket.IO events
def handle_tavern_message(data):
    player_id = session.get('user_id')
    if not player_id:
        return {'error': 'User not logged in'}

    character_id = data.get('character_id')
    chat_input = data.get('message')

    # Fetch character and check if it exists
    character = get_character_by_id(character_id)
    if character is None:
        return {'error': 'Character not found'}

    memories = get_memories(character_id, player_id)

    # Get response from the ChatGPT API
    response = send_chatgpt_api(character, chat_input, memories)

    # Parse the response to separate message and the flag
    response_message, has_name_question = parse_chat_response(response)


    # Check if character levels up
    check_and_level_up(character_id)

    # Return only the message to the chat interface
    return {'sender': character['name'], 'message': response_message}

def parse_chat_response(response):
    """
    Helper function to split the response and the Yes/No flag.
    Assumes the last word of the response is 'Yes' or 'No'.
    """
    response = response.strip()

    # Check if the last word is 'Yes' or 'No'
    if response.endswith('Yes.') or response.endswith('No.'):
        message = response[:-4].strip()  # Remove the last word ('Yes' or 'No')
        has_name_question = response[-3:].strip()  # Get 'Yes' or 'No'
    else:
        message = response  # No 'Yes' or 'No' detected, return full response
        has_name_question = "No"  # Default to "No" if neither is found
        
    print(f"message: {message}")

    return message, has_name_question


# Modify the tavern_chat route to work with both POST and GET methods
@characters_bp.route('/tavern_chat', methods=['POST', 'GET'])
def tavern_chat():
    player_id = session.get('user_id')
    if not player_id:
        return redirect(url_for('auth.login'))

    # Handle POST request (when form is submitted)
    if request.method == 'POST':
        character_id = request.form.get('character_id')
        
    # Handle GET request (in case the character_id is passed via URL query parameters)
    else:
        character_id = request.args.get('character_id')

    # Check if character_id is None after both GET and POST
    if not character_id:
        flash("No character selected for chat.", "danger")
        return redirect(url_for('characters.tavern_select'))

    # Fetch the character data using the character_id
    character = get_character_by_id(character_id)
    
    # Check if the character was found
    if character is None:
        flash("Character not found.", "danger")
        return redirect(url_for('characters.tavern_select'))

    return render_template('tavern_chat.html', character=character)




