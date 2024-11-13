import unittest
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import app, db, User, Watchlist


class WatchlistTests(unittest.TestCase):
    """Test suite for the watchlist functionality in RecommenderApp.

    This suite includes tests for:
    - Adding, removing, and viewing watchlist entries.
    - Handling duplicates and non-existent movies.
    - Checking watchlist entry limits.
    """

    def setUp(self):
        """Set up an application context, test client, and database for each test."""
        self.app = app
        self.app.config['TESTING'] = True
        # Use in-memory database for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create a test user and log them in
            self.test_user = User(
                username="tester",
                email="tester@example.com")
            self.test_user.set_password("password")
            db.session.add(self.test_user)
            db.session.commit()

            # Log in the user using the test client
            with self.client:
                self.client.post(
                    '/login',
                    data=dict(
                        username="tester",
                        password="password"))

    def tearDown(self):
        """Remove the database session and drop all tables after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_to_watchlist(self):
        """Test adding a movie to the watchlist.

        Verifies that a movie can be successfully added to the watchlist.
        """
        with self.client:
            response = self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"))
            # Redirect on successful addition
            self.assertEqual(response.status_code, 302)

            # Verify the movie was added to the watchlist
            watchlist_item = Watchlist.query.filter_by(
                user_id=self.test_user.id, movie_title="Inception").first()
            self.assertIsNotNone(watchlist_item,
                                 "Expected movie to be added to watchlist")

    def test_add_duplicate_to_watchlist(self):
        """Test adding a duplicate movie to the watchlist.

        Adds a movie to the watchlist, then attempts to add it again,
        expecting a flash message about duplication.
        """
        with self.client:
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"))
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"),
                follow_redirects=True)

            # Verify only one instance of the movie in the watchlist
            watchlist_items = Watchlist.query.filter_by(
                user_id=self.test_user.id, movie_title="Inception").all()
            self.assertEqual(
                len(watchlist_items),
                1,
                "Expected no duplicate entry in the watchlist")

    def test_remove_from_watchlist(self):
        """Test removing a movie from the watchlist.

        Adds a movie to the watchlist, then removes it and verifies
        successful removal.
        """
        with self.client:
            # Add a movie to remove
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"))
            watchlist_item = Watchlist.query.filter_by(
                user_id=self.test_user.id, movie_title="Inception").first()
            response = self.client.post(
                f'/remove_from_watchlist/{watchlist_item.id}')
            # Redirect on successful removal
            self.assertEqual(response.status_code, 302)

            # Verify removal from the watchlist
            watchlist_item = Watchlist.query.filter_by(
                user_id=self.test_user.id, movie_title="Inception").first()
            self.assertIsNone(watchlist_item,
                              "Expected movie to be removed from watchlist")

    def test_watchlist_view_empty(self):
        """Test viewing an empty watchlist.

        Verifies that an empty watchlist returns a message indicating no movies.
        """
        with self.client:
            response = self.client.get('/watchlist')
            self.assertIn(
                b'You have no movies in your watchlist.',
                response.data)

    def test_watchlist_view_nonempty(self):
        """Test viewing a non-empty watchlist.

        Adds a movie to the watchlist and verifies that it appears in the view.
        """
        with self.client:
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"))
            response = self.client.get('/watchlist')
            self.assertIn(b'Inception', response.data)

    def test_watchlist_limit(self):
        """Test the limit of entries in the watchlist.

        Adds multiple movies to the watchlist and verifies that the number
        of entries does not exceed a certain limit (assumed as 10 here).
        """
        with self.client:
            # Add exactly 10 unique items
            for i in range(10):
                self.client.post(
                    '/add_to_watchlist',
                    data=dict(
                        movie_title=f"Movie {i}",
                        imdb_rating="8.0"))

            # Check that there are exactly 10 items in the database
            watchlist_items = Watchlist.query.filter_by(
                user_id=self.test_user.id).all()
            self.assertEqual(
                len(watchlist_items),
                10,
                "Expected watchlist limit of 10")

    def test_watchlist_sorted_by_date(self):
        """Test sorting of watchlist entries by addition date.

        Adds movies in a specific order and verifies that the watchlist is
        sorted by the date added (newest first).
        """
        with self.client:
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Inception",
                    imdb_rating="8.8"))
            self.client.post(
                '/add_to_watchlist',
                data=dict(
                    movie_title="Interstellar",
                    imdb_rating="8.6"))

            # Fetch the watchlist items and verify order by timestamp
            watchlist_items = Watchlist.query.filter_by(
                user_id=self.test_user.id).order_by(
                Watchlist.id.desc()).all()
            titles = [item.movie_title for item in watchlist_items]

            self.assertEqual(
                titles, [
                    "Interstellar", "Inception"], "Expected sorting by date with the latest on top")


if __name__ == "__main__":
    unittest.main()
