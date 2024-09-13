from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit
from views.auth import auth_bp
from views.characters import characters_bp, handle_tavern_message
from database.db import init_db, add_columns_if_not_exist, insert_initial_characters, get_db_connection
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(characters_bp)

socketio = SocketIO(app)


# Helper function to convert Row object to dictionary
def row_to_dict(row):
    if row:
        return {key: row[key] for key in row.keys()}
    return {}


# Register the Socket.IO event handler
@socketio.on('send_message')
def socket_handle_message(data):
    response = handle_tavern_message(data)
    emit('receive_message', response)


def initialize_app():
    """
    Initialize the database and insert data. This should only run once when the app starts.
    """
    # Uncomment the following lines if you need to initialize the database on app start
    # with app.app_context():
    #    init_db()
    #    add_columns_if_not_exist()
    #    insert_initial_characters()
    pass  # Placeholder if no initialization is needed


@app.route('/game_select', methods=['GET', 'POST'])
def game_select():
    """
    Route to select a character for the game.
    Handles both displaying the selection and processing the selected character.
    """
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        c = conn.cursor()

        # Fetch characters belonging to the current player, including the 'class' field
        c.execute('''
            SELECT c.id, c.name, c.image_path, c.class
            FROM characters c
            JOIN player_characters pc ON c.id = pc.character_id
            WHERE pc.player_id = ?
        ''', (user_id,))

        characters = c.fetchall()
        conn.close()

        if request.method == 'POST':
            selected_character_id = request.form.get('character_id')
            if not selected_character_id:
                flash("No character selected.", "warning")
                return redirect(url_for('game_select'))

            # Fetch the selected character, including the 'class' field
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM characters WHERE id = ?', (selected_character_id,))
            character = c.fetchone()
            conn.close()

            if character:
                # Convert Row object to dictionary
                character_dict = row_to_dict(character)
                return render_template('game.html', character=character_dict)
            else:
                flash("Character not found.", "danger")
                return redirect(url_for('game_select'))

        # No need to convert list of Row objects if not using JSON serialization
        return render_template('game_select.html', characters=characters)
    else:
        return redirect(url_for('auth.login'))

@app.route('/start_game', methods=['POST'])
def start_game():
    """
    Route to start the game with the selected character.
    Redirects to the game page with the selected character's ID.
    """
    selected_character_id = request.form.get('character_id')
    if not selected_character_id:
        flash("No character selected to start the game.", "warning")
        return redirect(url_for('game_select'))

    # Redirect to the game route, passing the character ID as a query parameter
    return redirect(url_for('game', character_id=selected_character_id))

@app.route('/game')
def game():
    """
    Route to render the game page with the selected character.
    Converts the Row object to a dictionary for JSON serialization in the template.
    """
    character_id = request.args.get('character_id')

    if not character_id:
        flash("No character selected for the game.", "danger")
        return redirect(url_for('game_select'))

    conn = get_db_connection()
    c = conn.cursor()

    # Fetch the character's full data using the ID, including the 'class' field
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    conn.close()

    if not character:
        flash("Character not found.", "danger")
        return redirect(url_for('game_select'))

    # Convert Row object to dictionary
    character_dict = row_to_dict(character)

    return render_template('game.html', character=character_dict)

@app.route('/')
def index():
    """
    Home route that displays the user's information if logged in.
    """
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()

        # Convert Row object to dictionary for consistency (optional)
        user = row_to_dict(user)

    return render_template('index.html', user=user)


if __name__ == '__main__':
    # Prevent multiple initialization runs when the app auto-reloads
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        initialize_app()
    # Use socketio.run instead of app.run when using Flask-SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
