import pytest
from unittest.mock import MagicMock
import logging
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db, User, login_user

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Mock user data
mock_user = {
    'email': 'tesst@gmail.com',
    'pwd': "correctpassword", 
    'username': 'usernameused',
}

@pytest.fixture
def client():
    """Create a test client and initialize database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.app_context().push()
    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def mock_google_provider_cfg():
    """Mock the Google OAuth provider configuration."""
    return {
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    }


@pytest.fixture
def mock_token_response():
    """Mock the token response from Google."""
    return {
        "access_token": "fake-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "fake-refresh-token",
        "userinfo_endpoint": "",
        "token_endpoint": "https://oauth2.googleapis.com/token",
    }


@pytest.fixture
def mock_userinfo_response(email_verified=True):
    """Mock the user info response from Google."""
    return {
        "sub": "1234567890",
        "email": "testuser@gmail.com",
        "email_verified": email_verified,
        "given_name": "Test",
        "picture": "https://example.com/pic.jpg"
    }


@pytest.fixture
def insert_user():
    """Insert a mock user into the database."""
    user = User(username=mock_user['username'], email=mock_user['email'])
    user.set_password(mock_user['pwd'])
    db.session.add(user)
    db.session.commit()


def test_email_password_login_success_given_valid_credentials(client, insert_user):
    """Test login with valid credentials."""
    response = client.post(
        '/login',
        data={
            'username': mock_user['username'],
            'password': mock_user['pwd'],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_email_password_login_failure_given_invalid_email(client):
    """Test login with an invalid email."""
    response = client.post(
        '/login',
        data={
            'email': "invalid@gmail.com",
            'password': "wrongpassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 400
    assert b"Invalid username or password" in response.data
    assert b"Login" in response.data


def test_email_password_login_failure_given_incorrect_password(client, insert_user):
    """Test login with an incorrect password."""
    response = client.post('/login', data={
        'username': mock_user['email'],
        'password': "wrongpassword"
    })
    assert response.status_code == 400


def test_redirect_to_google_page(client):
    """Test the redirect to Google's login page."""
    response = client.get('/google-login')
    assert response.status_code == 302


@pytest.mark.usefixtures("mocker")
def test_google_login_callback_unverified_email(client, mocker, mock_google_provider_cfg, mock_token_response, mock_userinfo_response):
    """
    Test google_login_callback when the email is unverified, mocking implementation.
    """
    def mock_get_impl(url, *args, **kwargs):
        if "userinfo_endpoint" in url:
            return MagicMock(
                status_code=200,
                json=lambda: mock_userinfo_response(email_verified=False)
            )
        return MagicMock(
            status_code=200,
            json=lambda: mock_google_provider_cfg
        )

    def mock_post_impl(url, *args, **kwargs):
        if "token_endpoint" in url:
            return MagicMock(
                status_code=200,
                json=lambda: mock_token_response
            )
        return MagicMock(status_code=400, json=lambda: {"error": "Invalid request"})

    mocker.patch('requests.get', side_effect=mock_get_impl)
    mocker.patch('requests.post', side_effect=mock_post_impl)

    response = client.get('/login/callback?code=fake-auth-code')

    assert response.status_code == 400



@pytest.mark.usefixtures("mocker")
def test_login_redirect_if_authenticated(client, mocker):
    """
    Test that the user is redirected to the landing page if they are already logged in.
    """

    user = User(username="testuser", email="testuser@example.com")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = user.id  

    response = client.get('/login')

    assert response.status_code == 200  # Redirect


@pytest.mark.usefixtures("mocker")
def test_edit_profile_redirects_if_not_authenticated(client):
    """
    Test that an unauthenticated user is redirected to the login page.
    """
    response = client.post('/edit_profile', data={'favorite_genres': 'Rock, Pop'})

    assert response.status_code == 302  
    assert response.location.__contains__('/login')  

@pytest.mark.usefixtures("mocker")
def test_edit_profile_success(client):
    """
    Test that an authenticated user can update their profile.
    """

    user = User(username="testuser", email="testuser@example.com")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()


    with client.session_transaction() as sess:
        sess['user_id'] = user.id

    response = client.post('/login', data={
        'username': "testuser",
        'password': "password"
    })

    response = client.post('/edit_profile', data={'favorite_genres': 'Rock, Pop'})


    assert response.status_code == 302  

    updated_user = User.query.filter_by(id=user.id).first()
    assert updated_user.favorite_genres == 'Rock, Pop'

    with client.session_transaction() as sess:
        flashes = list(sess['_flashes']) 
        assert ('success', 'Profile updated successfully!') in flashes
        
def test_edit_profile_unauthenticated(client):
    """
    Test that an unauthenticated user is redirected to the login page 
    when trying to access the /edit_profile route.
    """
    response = client.get('/edit_profile')

    assert response.status_code != 200 


@pytest.fixture
def auth(client):
    """Fixture to handle user authentication."""
    def login(username='testuser', password='correctpassword'):
        """Helper function to log in a user."""
        user = User(username=username, email='testuser@example.com')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        response = client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)
        return response

    yield login

def test_register_new_user(client):
    """
    Test the registration of a new user with valid details.
    """
    response = client.post(
        '/register',
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword'
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b'Welcome, newuser' in response.data 

def test_change_password_success(client, auth):
    """
    Test successful password change by an authenticated user.
    """
    auth(username="testuser", password="oldpassword")

    response = client.post(
        '/change_password',
        data={"new_password": "newsecurepassword"},
        follow_redirects=True
    )


    assert response.status_code == 200

    with client.session_transaction() as sess:
        flashes = list(sess['_flashes']) 
        assert ('success', 'Password changed successfully!') in flashes


def test_change_password_empty_password(client, auth):
    """
    Test attempting to change the password to an empty value.
    """
    auth(username="testuser", password="oldpassword")

    response = client.post(
        '/change_password',
        data={"new_password": ""},
        follow_redirects=True
    )

    assert response.status_code == 200
    with client.session_transaction() as sess:
        flashes = list(sess['_flashes']) 
        assert ('danger', 'Password cannot be empty!') in flashes


def test_change_password_unauthenticated_user(client):
    """
    Test that an unauthenticated user cannot change the password.
    """
    response = client.post(
        '/change_password',
        data={"new_password": "newsecurepassword"},
        follow_redirects=True
    )

    assert response.status_code == 200
    with client.session_transaction() as sess:
        flashes = list(sess['_flashes']) 
        assert ('message', 'Please log in to access this page.') in flashes

def test_change_password_no_data(client, auth):
    """
    Test changing the password when no data is sent in the form.
    """
    # Log in as a test user
    auth(username="testuser", password="oldpassword")

    response = client.post('/change_password', data={}, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as sess:
        flashes = list(sess['_flashes']) 
        assert ('danger', 'Password cannot be empty!') in flashes

def test_change_password_no_db_changes(client, auth):
    """
    Ensure the database remains unchanged when no password is provided.
    """
    auth(username="testuser", password="oldpassword")

    user = db.session.query(User).filter_by(username="testuser").first()
    original_password_hash = user.password_hash

    client.post('/change_password', data={"new_password": ""}, follow_redirects=True)
    db.session.refresh(user)

    assert user.password_hash == original_password_hash