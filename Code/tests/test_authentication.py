import pytest
import sys
from .utils import client
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db, User




def register(client, username, email, password):
    """Helper function to register a user."""
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password
    }, follow_redirects=True)


def login(client, username, password):
    """Helper function to log in a user."""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def logout(client):
    """Helper function to log out a user."""
    return client.get('/logout', follow_redirects=True)


def test_register_new_user(client):
    """Test registering a new user."""
    response = client.post('/register', data={
        'username': "newuser",
        'email': "newuser@example.com",
        'password': "password123"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_register_existing_user(client):
    """Test registering a user with an existing username or email."""

    username = "newuser"
    email = "newuser@example.com"
    password = "password123"
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    response = client.post(
        '/register',
        data={
            'username': username,
            'email': email,
            'password': password,
        },
        follow_redirects=True,
    )

    assert response.status_code == 400



def test_successful_login(client):
    """Test successful login."""
    register(client, "testuser", "testuser@example.com", "password123")
    response = login(client, "testuser", "password123")
    assert response.status_code == 200


def test_login_nonexistent_user(client):
    """Test login attempt with a nonexistent username."""
    response = login(client, "nonexistentuser", "password123")
    assert response.status_code == 400


def test_login_wrong_password(client):
    """Test login failure with incorrect password."""
    register(client, "testuser2", "testuser2@example.com", "password123")
    response = login(client, "testuser2", "wrongpassword")
    assert response.status_code == 200


def test_successful_logout(client):
    """Test successful logout."""
    username = "logoutuser"
    email = "logoutuser@example.com"
    password = "password123"

    # Register, login, and logout sequence
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    #register(client, username, email, password)
    response = login(client, username, password)
    assert response.status_code == 200
    response = logout(client)

    assert response.status_code == 200

