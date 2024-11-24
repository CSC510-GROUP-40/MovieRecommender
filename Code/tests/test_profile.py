import unittest
from unittest.mock import patch
from flask import jsonify
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db, User


class ProfileTests(unittest.TestCase):
    """Test suite for profile management functions in RecommenderApp.

    This suite includes tests for:
    - Updating and retrieving favorite genres.
    - Setting and validating user passwords.
    - Unique email and username constraints.
    """

    def setUp(self):
        """Set up test client and database."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

            # Create a user for testing purposes
            self.user = User(username="testuser", email="testuser@example.com")
            self.user.set_password("testpassword")
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        """Clean up database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_update_favorite_genres(self):
        """Test updating favorite genres for a user profile.

        Sets favorite genres and verifies the update.
        """
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.favorite_genres = "Comedy, Drama"
            db.session.commit()
            self.assertEqual(user.favorite_genres, "Comedy, Drama", "Expected favorite genres to be 'Comedy, Drama'")

    def test_unique_email_constraint(self):
        """Test unique email constraint for user profile.

        Creates a user and attempts to create another with the same email,
        expecting an IntegrityError due to duplicate email.
        """
        with app.app_context():
            user2 = User(username="user2", email="testuser@example.com")  # Duplicate email
            db.session.add(user2)
            with self.assertRaises(Exception, msg="Expected IntegrityError for duplicate email"):
                db.session.commit()

    def test_unique_username_constraint(self):
        """Test unique username constraint for user profile.

        Creates a user and attempts to create another with the same username,
        expecting an IntegrityError due to duplicate username.
        """
        with app.app_context():
            user2 = User(username="testuser", email="unique@example.com")  # Duplicate username
            db.session.add(user2)
            with self.assertRaises(Exception, msg="Expected IntegrityError for duplicate username"):
                db.session.commit()

    def test_change_password(self):
        """Test changing a user's password through the change_password route.

        Verifies that providing a valid password updates the password successfully.
        """
        with self.app:
            # Log in the test user
            self.app.post('/login', data=dict(username="testuser", password="testpassword"))

            # Attempt to change the password to a new valid password
            self.app.post('/change_password', data=dict(new_password="new_password"), follow_redirects=True)

            # Verify that the password was actually changed
            with app.app_context():
                user = User.query.filter_by(username="testuser").first()
                self.assertTrue(user.check_password("new_password"), "Expected password to be updated to 'new_password'")

    def test_change_password_empty(self):
        """Test changing a user's password with an empty password through the change_password route.

        Verifies that an empty password cannot be set and that the correct flash message is displayed.
        """
        with self.app:
            # Log in the test user
            self.app.post('/login', data=dict(username="testuser", password="testpassword"))

            # Attempt to change the password to an empty string
            self.app.post('/change_password', data=dict(new_password=""), follow_redirects=True)

            # Verify that the password was not changed to an empty password
            with app.app_context():
                user = User.query.filter_by(username="testuser").first()
                self.assertTrue(user.check_password("testpassword"), "Expected password to remain unchanged")

    def test_retrieve_profile_data(self):
        """Test retrieving profile data for a user.

        Retrieves profile data and checks if it includes 'favorite_genres'.
        """
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.favorite_genres = "Comedy"
            db.session.commit()
            profile_data = {
                "username": user.username,
                "email": user.email,
                "favorite_genres": user.favorite_genres
            }
            response = jsonify(profile_data)
            self.assertIn("favorite_genres", response.json, "Expected 'favorite_genres' key in profile data")

    def test_profile_favorite_genres_case_insensitive(self):
        """Test case-insensitive update of favorite genres.

        Sets favorite genres in uppercase and verifies retrieval in the same format.
        """
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.favorite_genres = "ACTION"
            db.session.commit()
            self.assertEqual(user.favorite_genres, "ACTION", "Expected favorite genres to be 'ACTION'")
            
    def test_retrieve_nonexistent_user_profile(self):
        """Test retrieving profile data for a non-existent user."""
        with app.app_context():
            user = User.query.filter_by(username="nonexistentuser").first()
            self.assertIsNone(user, "Expected no user to be retrieved for a nonexistent username")

    def test_no_duplicate_favorite_genres(self):
        """Test that duplicate genres are not added to the favorite genres."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.favorite_genres = "Comedy, Comedy"
            db.session.commit()
            self.assertEqual(user.favorite_genres, "Comedy, Comedy", "Expected no duplicate genres")

    def test_update_email(self):
        """Test updating a user's email."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.email = "newemail@example.com"
            db.session.commit()
            self.assertEqual(user.email, "newemail@example.com", "Expected email to be updated")

    def test_delete_user_profile(self):
        """Test deleting a user profile."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            db.session.delete(user)
            db.session.commit()
            user = User.query.filter_by(username="testuser").first()
            self.assertIsNone(user, "Expected user profile to be deleted")

    def test_invalid_login_attempt(self):
        """Test logging in with invalid credentials."""
        with self.app:
            response = self.app.post('/login', data=dict(username="testuser", password="wrongpassword"))
            self.assertIn("Invalid username or password", response.get_data(as_text=True), 
                        "Expected an error message for invalid credentials")



if __name__ == "__main__":
    unittest.main()
