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
    with app.app_context():
        init_db()
        add_columns_if_not_exist()
        insert_initial_characters()

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
