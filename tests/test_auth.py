import os
import tempfile
import pytest
from flask import Flask
from app import app  # assuming your Flask app is named 'app.py'
from views.auth import auth_bp  # importing your auth blueprint

@pytest.fixture
def client():
    # Set up a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for easier testing

    # Create a test client
    with app.test_client() as client:
        with app.app_context():
            # Initialize the database schema
            app.init_db()
        yield client

    # Teardown: close and remove the temp database
    os.close(db_fd)
    os.unlink(db_path)

def test_signup_existing_username(client):
    """Test flash message when signing up with an existing username."""
    
    # Simulate a signup request with an existing username
    response = client.post('/signup', data={
        'username': 'existing_user', 
        'password': 'password123',
        'profile_picture': (BytesIO(b'my picture'), 'profile.png')
    }, follow_redirects=True)

    # Check if the correct flash message was displayed
    assert b"Username already exists. Please choose another one." in response.data

