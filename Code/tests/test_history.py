import unittest
from flask_login import login_user
from datetime import datetime
import sys
sys.path.append('../recommenderapp')

from recommenderapp.app import app, db, User, Recommendation


class HistoryTests(unittest.TestCase):
    """Test suite for the history functionality in RecommenderApp."""

    def setUp(self):
        """Set up test client and initialize database."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
            # Create a user and log them in
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        """Tear down database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_user(self):
        """Helper function to log in the user for the test session."""
        self.app.post('/login', data=dict(
            username="testuser",
            password="password"
        ), follow_redirects=True)

    def test_view_empty_history(self):
        """Test viewing an empty recommendation history."""
        self.login_user()
        response = self.app.get('/history', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No recommendations found', response.data)

    def test_view_nonempty_history(self):
        """Test viewing a non-empty recommendation history."""
        with app.app_context():
            recommendation = Recommendation(
                user_id=self.user_id,
                movie_title="Inception",
                recommended_on=datetime.utcnow()
            )
            db.session.add(recommendation)
            db.session.commit()

        self.login_user()
        response = self.app.get('/history', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inception', response.data)

    def test_multiple_recommendations_history(self):
        """Test viewing history with multiple recommendations."""
        with app.app_context():
            rec1 = Recommendation(
                user_id=self.user_id,
                movie_title="Inception",
                recommended_on=datetime.utcnow()
            )
            rec2 = Recommendation(
                user_id=self.user_id,
                movie_title="The Matrix",
                recommended_on=datetime.utcnow()
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

        self.login_user()
        response = self.app.get('/history', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inception', response.data)
        self.assertIn(b'The Matrix', response.data)
