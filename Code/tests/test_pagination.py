from re import A
import unittest
from unittest.mock import patch, MagicMock
import sys
import json
from flask import session
from flask_login import current_user, login_user, logout_user
sys.path.append('../recommenderapp')  # Adjust the path to the location of your app

from recommenderapp.app import app, db, Movie, User, Recommendation, get_movie_info, send_request_to_omdb

class PaginationTests(unittest.TestCase):
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

    def tearDown(self):
        """
        Tear down database after each test.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_movie_class_instantiation(self):
        """
        Test that Movie class can be instantiated and to_dict works correctly.
        """
        movie = Movie(
            title="Inception",
            poster="some_url",
            rating=8.8,
            genres="Action, Sci-Fi",
            cast="Leonardo DiCaprio",
            imdb_id="tt1375666",
            plot="A thief...")
        movie_dict = movie.to_dict()
        self.assertEqual(movie_dict['title'], "Inception")
        self.assertEqual(movie_dict['poster'], "some_url")
        self.assertEqual(movie_dict['rating'], 8.8)
        self.assertEqual(movie_dict['genres'], "Action, Sci-Fi")
        self.assertEqual(movie_dict['cast'], "Leonardo DiCaprio")
        self.assertEqual(movie_dict['imdb_id'], "tt1375666")
        self.assertEqual(movie_dict['plot'], "A thief...")

    @patch('app.requests.get')
    def test_send_request_to_omdb_valid(self, mock_get):
        """
        Test that send_request_to_omdb returns valid data when given a correct movie title.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Title": "Inception",
            "Year": "2010",
            "imdbRating": "8.8",
            "Genre": "Action, Adventure, Sci-Fi",
            "Poster": "some_poster_url",
            "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt",
            "imdbID": "tt1375666",
            "Plot": "A thief..."
        }
        mock_get.return_value = mock_response
        movie_info = send_request_to_omdb("Movie 1")
        self.assertIsNotNone(movie_info)
        self.assertEqual(movie_info['Title'], "Inception")
    
    @patch('app.requests.get')
    def test_get_movie_info_valid(self, mock_get):
        """
        Test that get_movie_info returns the expected dictionary when given a valid title.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Response": "True",
            "Title": "Source Code",
            "Year": "2010",
            "imdbRating": "8.8",
            "Genre": "Action, Adventure, Sci-Fi",
            "Poster": "some_poster_url",
            "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt",
            "imdbID": "tt1375666",
            "Plot": "A thief..."
        }
        mock_get.return_value = mock_response
        movie_info = get_movie_info("Movie 1")
        self.assertIsNotNone(movie_info)
        self.assertEqual(movie_info['Title'], 'Source Code')

    @patch('app.requests.get')
    def test_get_movie_info_invalid(self, mock_get):
        """
        Test that get_movie_info returns None when the movie is not found.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Movie not found!"
        }
        mock_get.return_value = mock_response
        movie_info = get_movie_info("Movie 1")
        self.assertIsNone(movie_info)
    
    def test_predict_valid_data(self):
        """
        Test that predict route handles valid data and returns expected recommendations.
        """

        data = {'movie_list': ["Rubber (2010)", "Toy Story (1995)"]}
        
        # Make the POST request within the context
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('recommendations', response_data)
        self.assertEqual(len(response_data['recommendations']), 20)
    
    def test_predict_empty_movie_list(self):
        """
        Test that predict route handles empty movie_list in data.
        """
        data = {'movie_list': []}
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('recommendations', response_data)
        self.assertEqual(len(response_data['recommendations']), 0)
    
    
    @patch('recommenderapp.app.get_movie_info')
    @patch('recommenderapp.app.recommendForNewUser')
    def test_predict_skips_invalid_movies(self, mock_recommend, mock_get_info):
        """
        Test that predict route skips movies with invalid info.
        """
        # Mock the recommendation function to return both valid and invalid movies
        mock_recommend.return_value = ['ValidMovie', 'InvalidMovie']
        
        # Mock get_movie_info to return valid data for 'ValidMovie' and None for 'InvalidMovie'
        mock_get_info.side_effect = [
            {
                'Title': 'ValidMovie',
                'imdbRating': '7.0',
                'Genre': 'Drama',
                'Poster': 'valid_poster_url',
                'Actors': 'Actor A',
                'imdbID': 'tt1234567',
                'Plot': 'Some plot...',
                'Response': 'True'
            },
            None  # 'InvalidMovie' will return None, simulating invalid movie info
        ]
        
        data = {'movie_list': ['Movie1', 'Movie2']}
        
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
                
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        response_data = json.loads(response.data)
        
        # Assert that only one recommendation is returned (the valid one)
        self.assertEqual(len(response_data['recommendations']), 1)
        self.assertEqual(response_data['recommendations'][0]['title'], 'ValidMovie')

    @patch('recommenderapp.app.get_movie_info')
    @patch('recommenderapp.app.recommendForNewUser')
    def test_recommendations_saved_to_db(self, mock_recommend, mock_get_info):
        """
        Test that recommendations are saved in the database.
        """
        mock_recommend.return_value = ['Inception']
        mock_get_info.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'Leonardo DiCaprio, Joseph Gordon-Levitt',
            'imdbID': 'tt1375666',
            'Plot': 'A thief...',
            'Response': 'True'
        }
        data = {'movie_list': ['Movie1']}
        self.client.post('/predict', data=json.dumps(data), content_type='application/json')

        # Check that the recommendation was saved in the database
        recommendation = Recommendation.query.filter_by(user_id=self.user_id, movie_title='Inception').first()
        self.assertIsNotNone(recommendation)
    
    def test_correct_number_of_recommendations(self):
        """
        Test that the correct number of recommendations is returned.
        """

        data = {'movie_list': ['Inception (2010)']}
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data['recommendations']), 23)

    @patch('recommenderapp.app.get_movie_info')
    @patch('recommenderapp.app.recommendForNewUser')
    def test_recommendation_format(self, mock_recommend, mock_get_info):
        """
        Test that the movie info in the recommendations matches the expected format.
        """
        mock_recommend.return_value = ['Inception']
        mock_get_info.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'Leonardo DiCaprio, Joseph Gordon-Levitt',
            'imdbID': 'tt1375666',
            'Plot': 'A thief...',
            'Response': 'True'
        }
        data = {'movie_list': ['Movie1']}
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        response_data = json.loads(response.data)
        recommendation = response_data['recommendations'][0]
        self.assertIn('title', recommendation)
        self.assertIn('poster', recommendation)
        self.assertIn('rating', recommendation)
        self.assertIn('genres', recommendation)
        self.assertIn('cast', recommendation)
        self.assertIn('imdb_id', recommendation)
        self.assertIn('plot', recommendation)
    
    @patch('app.requests.get')
    def test_send_request_to_omdb_invalid_api_key(self, mock_get):
        """
        Test that send_request_to_omdb returns None when API key is invalid.
        """
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Invalid API key!"
        }
        mock_get.return_value = mock_response
        movie_info = send_request_to_omdb("Inception (2010)")
        self.assertIsNone(movie_info)

    @patch('app.requests.get')
    def test_get_movie_info_malformed_response(self, mock_get):
        """
        Test that get_movie_info returns None when the response from OMDB is malformed.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = None  # Malformed response
        mock_get.return_value = mock_response
        movie_info = get_movie_info("Inception (2010)")
        self.assertIsNone(movie_info)

    def test_predict_non_json_data(self):
        """
        Test that predict route returns 400 when request data is not JSON.
        """
        response = self.client.post('/predict', data="Not a JSON", content_type='text/plain')
        self.assertEqual(response.status_code, 400)
    
    def test_predict_no_logged_in_user(self):
        """
        Test that predict route fails when no user is logged in.
        """
        # Ensure no user is logged in
        self.client.get('/logout')

        data = {'movie_list': ['Inception (2010)']}
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')

        # Assert that the response status code is 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        self.client.post('/login', data=dict(username="tester", password="password"))

    @patch('recommenderapp.app.db.session.add')
    @patch('recommenderapp.app.get_movie_info')
    @patch('recommenderapp.app.recommendForNewUser')
    def test_db_add_exception(self, mock_recommend, mock_get_info, mock_db_add):
        """
        Test that adding a recommendation to the database fails when db.session.add() raises an exception.
        """
        mock_recommend.return_value = ['Inception']
        mock_get_info.return_value = {
            'Title': 'Inception',
            'imdbRating': '8.8',
            'Genre': 'Action, Adventure, Sci-Fi',
            'Poster': 'some_poster_url',
            'Actors': 'Leonardo DiCaprio, Joseph Gordon-Levitt',
            'imdbID': 'tt1375666',
            'Plot': 'A thief...',
            'Response': 'True'
        }
        mock_db_add.side_effect = Exception("Database add failed")
        data = {'movie_list': ['Movie1']}
        response = self.client.post('/predict', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 500)

if __name__ == "__main__":
    unittest.main()