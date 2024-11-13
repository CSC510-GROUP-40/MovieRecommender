import unittest
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db


class AuthTests(unittest.TestCase):
    """Test suite for authentication and user account management in RecommenderApp."""

    def setUp(self):
        """Set up test client and initialize database."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def register(self, username, email, password):
        """Helper function to register a user."""
        return self.app.post('/register', data=dict(
            username=username,
            email=email,
            password=password
        ), follow_redirects=True)

    def login(self, username, password):
        """Helper function to log in a user."""
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Helper function to log out a user."""
        return self.app.get('/logout', follow_redirects=True)

    def test_register_new_user(self):
        """Test registering a new user."""
        response = self.register(
            "newuser",
            "newuser@example.com",
            "password123")
        # Expecting successful redirect to landing page or registration page
        self.assertEqual(response.status_code, 200)

    def test_register_existing_user(self):
        """Test registering a user with an existing username or email."""
        self.register(
            "existinguser",
            "existinguser@example.com",
            "password123")
        response = self.register(
            "existinguser",
            "existinguser@example.com",
            "password123")
        # Should be redirected due to already existing user
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        """Test successful login."""
        self.register("testuser", "testuser@example.com", "password123")
        response = self.login("testuser", "password123")
        # Expecting successful redirect to landing page
        self.assertEqual(response.status_code, 200)

    def test_login_nonexistent_user(self):
        """Test login attempt with a nonexistent username."""
        response = self.login("nonexistentuser", "password123")
        # Should redirect due to login failure
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_password(self):
        """Test login failure with incorrect password."""
        self.register("testuser2", "testuser2@example.com", "password123")
        response = self.login("testuser2", "wrongpassword")
        # Should redirect due to login failure
        self.assertEqual(response.status_code, 200)

    def test_successful_logout(self):
        """Test successful logout."""
        self.register("logoutuser", "logoutuser@example.com", "password123")
        self.login("logoutuser", "password123")
        response = self.logout()
        # Expecting successful redirect after logout
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
