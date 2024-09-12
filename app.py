from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from views.auth import auth_bp
from views.characters import characters_bp, handle_tavern_message
from database.db import init_db, add_columns_if_not_exist, insert_initial_characters, get_db_connection
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(characters_bp)

socketio = SocketIO(app)


# Register the Socket.IO event handler
@socketio.on('send_message')
def socket_handle_message(data):
    response = handle_tavern_message(data)
    emit('receive_message', response)
    
def initialize_app():
    """
    Initialize the database and insert data. This should only run once when the app starts.
    """
    # with app.app_context():
    #    init_db()
        #add_columns_if_not_exist()
        #insert_initial_characters()
        
@app.route('/game_select')
def select_character():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        c = conn.cursor()
        
        # Query characters only for the logged-in user
        c.execute('''
            SELECT c.id, c.name, c.image_path 
            FROM characters c
            JOIN player_characters pc ON c.id = pc.character_id
            WHERE pc.player_id = ?
        ''', (user_id,))
        
        characters = c.fetchall()
        conn.close()
        
        return render_template('game_select.html', characters=characters)
    else:
        return redirect(url_for('login'))


@app.route('/start_game', methods=['POST'])
def start_game():
    selected_character_id = request.form['character_id']
    
    # Redirect to the game route, passing the character ID as a query parameter
    return redirect(url_for('game', character_id=selected_character_id))




@app.route('/game')
def game():
    character_id = request.args.get('character_id')

    if not character_id:
        return redirect(url_for('game_select'))

    conn = get_db_connection()
    c = conn.cursor()

    # Fetch the character's full data using the ID
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    conn.close()

    if not character:
        return redirect(url_for('game_select'))

    return render_template('game.html', character=character)


@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
    return render_template('index.html', user=user)

if __name__ == '__main__':
    # Prevent multiple initialization runs when the app auto-reloads
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5001)


