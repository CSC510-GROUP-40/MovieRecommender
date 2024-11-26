from re import A
import unittest
from unittest.mock import patch, MagicMock
import sys
import json
from flask import session
from flask_login import current_user, login_user, logout_user
sys.path.append('../recommenderapp')  # Adjust the path to the location of your app

from recommenderapp.app import app, db, Movie, User, Recommendation, get_movie_info, send_request_to_omdb

class MovieDetailsTests(unittest.TestCase):
    """
    Test cases for pagination functionality.
    """
    def setUp(self) -> None:
        """
        Set up an application context, test client, and database for each test.
        """
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
            self.user_id = self.test_user.id

            # Log in the user using the test client
            with self.client:
                self.client.post(
                    '/login',
                    data=dict(
                        username="tester",
                        password="password"))
    
    def test_movie_to_dict_includes_all_fields(self):
        """
        Test that Movie.to_dict() includes all fields.
        """
        movie = Movie(
            title='Inception',
            poster='some_poster_url',
            rating='8.8',
            genres='Action, Adventure, Sci-Fi',
            cast='Leonardo DiCaprio, Joseph Gordon-Levitt',
            imdb_id='tt1375666',
            plot='A thief who steals corporate secrets...'
        )

        movie_dict = movie.to_dict()

        expected_keys = {'title', 'poster', 'rating', 'genres', 'cast', 'imdb_id', 'plot'}
        self.assertEqual(set(movie_dict.keys()), expected_keys)
        self.assertEqual(movie_dict['title'], 'Inception')
        self.assertEqual(movie_dict['cast'], 'Leonardo DiCaprio, Joseph Gordon-Levitt')
        self.assertEqual(movie_dict['imdb_id'], 'tt1375666')
        self.assertEqual(movie_dict['plot'], 'A thief who steals corporate secrets...')
    
    @patch('recommenderapp.app.recommendForNewUser')
    @patch('recommenderapp.app.get_movie_info')
    def test_predict_route_returns_full_movie_info(self, mock_get_movie_info, mock_recommend):
        """
        Test that the /predict route returns recommendations with all movie info fields.
        """
        mock_recommend.return_value = ['Inception']
        mock_get_movie_info.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'Leonardo DiCaprio, Joseph Gordon-Levitt',
            'imdbID': 'tt1375666',
            'Plot': 'A thief who steals corporate secrets...',
            'Response': 'True'
        }

        data = {'movie_list': ['Movie1']}

        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        recommendation = response_data['recommendations'][0]

        expected_keys = {'title', 'poster', 'rating', 'genres', 'cast', 'imdb_id', 'plot'}
        self.assertEqual(set(recommendation.keys()), expected_keys)
        self.assertEqual(recommendation['title'], 'Inception')
        self.assertEqual(recommendation['cast'], 'Leonardo DiCaprio, Joseph Gordon-Levitt')
        self.assertEqual(recommendation['imdb_id'], 'tt1375666')
        self.assertEqual(recommendation['plot'], 'A thief who steals corporate secrets...')
    
    @patch('recommenderapp.app.send_request_to_omdb')
    def test_get_movie_info_missing_fields(self, mock_send_request):
        """Test that get_movie_info returns None when required fields are missing."""
        # Simulate missing 'Actors' field
        mock_send_request.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'N/A',  # Missing cast information
            'imdbID': 'tt1375666',
            'Plot': 'A thief who steals corporate secrets...',
            'Response': 'True'
        }

        movie_info = get_movie_info('Inception')
        self.assertIsNone(movie_info)
    
    @patch('recommenderapp.app.requests.get')
    def test_send_request_to_omdb_retrieves_all_fields(self, mock_requests_get):
        """Test that send_request_to_omdb retrieves all necessary fields from OMDb."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'Leonardo DiCaprio, Joseph Gordon-Levitt',
            'imdbID': 'tt1375666',
            'Plot': 'A thief who steals corporate secrets...',
            'Response': 'True'
        }
        mock_requests_get.return_value = mock_response

        movie_info = send_request_to_omdb('Inception')

        expected_keys = {'Title', 'imdbRating', 'Genre', 'Poster', 'Actors', 'imdbID', 'Plot', 'Response'}
        self.assertEqual(set(movie_info.keys()), expected_keys)
        self.assertEqual(movie_info['Actors'], 'Leonardo DiCaprio, Joseph Gordon-Levitt')
        self.assertEqual(movie_info['imdbID'], 'tt1375666')
        self.assertEqual(movie_info['Plot'], 'A thief who steals corporate secrets...')
    
    @patch('recommenderapp.app.send_request_to_omdb')
    def test_predict_malformed_omdb_response(self, mock_send_request):
        """Test that predict route fails gracefully when OMDb returns malformed data."""
        
        # Mock send_request_to_omdb to return a malformed response
        mock_send_request.return_value = {
            'Title': 'InvalidMovie',
            'imdbRating': 'N/A',  # Invalid rating
            'Genre': 'N/A',       # Invalid genre
            'Poster': 'N/A',      # Invalid poster URL
            'Actors': None,       # Missing cast information
            'imdbID': None,       # Missing IMDb ID
            'Plot': None,         # Missing plot
            'Response': 'True'    # OMDb claims the response is valid
        }
        
        data = {'movie_list': ['InvalidMovie']}
        
        # Make a POST request to the predict route
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200, "Predict route should handle gracefully for malformed OMDb response.")
        
        # Optionally, check that no recommendations were returned
        response_data = json.loads(response.data)
        print(response_data)
        self.assertEqual(len(response_data['recommendations']), 0, "No recommendations should be returned for malformed OMDb response.")

    def tearDown(self):
        """
        Tear down database after each test.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    unittest.main()