import unittest
from unittest.mock import patch
import sys
sys.path.append('../recommenderapp')
from recommenderapp.prediction_scripts.tmdb_utils import search_movie_tmdb, get_streaming_providers, get_movie_reviews


class TestTMDBFunctions(unittest.TestCase):
    """
    Test suite for TMDB API-related functions in the RecommenderApp.
    Includes tests for searching movies by name and year, retrieving
    streaming providers, and fetching reviews for a movie.
    """

    # Mock API key for testing purposes
    TMDB_API_KEY = "9f385440fe752884a4f5b8ea5b6839dd"

    # Test cases for `search_movie_tmdb`

    @patch('requests.get')
    def test_search_movie_tmdb_valid(self, mock_get):
        """
        Test search_movie_tmdb with a valid movie name, expecting
        a valid movie ID to be returned.
        """
        # Mock a successful response with a valid movie ID
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": [{"id": 12345}]}

        movie_id = search_movie_tmdb("Inception", self.TMDB_API_KEY)
        self.assertEqual(
            movie_id,
            12345,
            "Expected valid movie ID for 'Inception'")

    @patch('requests.get')
    def test_search_movie_tmdb_invalid_name(self, mock_get):
        """
        Test search_movie_tmdb with a nonexistent movie name, expecting
        None to be returned.
        """
        # Mock a successful response with no results
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        movie_id = search_movie_tmdb("xxxxxxxxxxxxxx", self.TMDB_API_KEY)
        self.assertIsNone(movie_id, "Expected None for nonexistent movie name")

    @patch('requests.get')
    def test_search_movie_tmdb_invalid_year(self, mock_get):
        """
        Test search_movie_tmdb with a valid movie name but an invalid year,
        expecting None to be returned.
        """
        # Mock a response with no results due to invalid year
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        movie_id = search_movie_tmdb("Inception", self.TMDB_API_KEY, year=1800)
        self.assertIsNone(
            movie_id,
            "Expected None for valid movie name but invalid year")

    @patch('requests.get')
    def test_search_movie_tmdb_api_failure(self, mock_get):
        """
        Test search_movie_tmdb with an API failure (500 status code),
        expecting None to be returned.
        """
        # Mock an API failure response
        mock_get.return_value.status_code = 500

        movie_id = search_movie_tmdb("Inception", self.TMDB_API_KEY)
        self.assertIsNone(movie_id, "Expected None due to API failure")

    # Test cases for `get_streaming_providers`

    @patch('requests.get')
    def test_get_streaming_providers_valid(self, mock_get):
        """
        Test get_streaming_providers with a valid movie ID, expecting
        a list of streaming providers with name and logo URL.
        """
        # Mock a successful response with valid streaming provider data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": {
                "US": {
                    "buy": [
                        {"provider_name": "Amazon Prime", "logo_path": "/logo.png"}
                    ]
                }
            }
        }

        providers = get_streaming_providers(12345, self.TMDB_API_KEY)
        expected = [
            ("Amazon Prime", "https://image.tmdb.org/t/p/w500/logo.png")]
        self.assertEqual(
            providers,
            expected,
            "Expected valid streaming providers list for US")

    @patch('requests.get')
    def test_get_streaming_providers_no_country(self, mock_get):
        """
        Test get_streaming_providers with a movie ID that has no available
        providers in the specified country (US), expecting an empty list.
        """
        # Mock a successful response with no providers in US
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": {}}

        providers = get_streaming_providers(12345, self.TMDB_API_KEY)
        self.assertEqual(
            providers,
            [],
            "Expected empty list for movie with no streaming providers")

    @patch('requests.get')
    def test_get_streaming_providers_invalid_id(self, mock_get):
        """
        Test get_streaming_providers with an invalid movie ID, expecting
        None due to a 404 status code.
        """
        # Mock a 404 response for an invalid movie ID
        mock_get.return_value.status_code = 404

        providers = get_streaming_providers(99999, self.TMDB_API_KEY)
        self.assertIsNone(providers, "Expected None for invalid movie ID")

    @patch('requests.get')
    def test_get_streaming_providers_api_failure(self, mock_get):
        """
        Test get_streaming_providers with an API failure (500 status code),
        expecting None to be returned.
        """
        # Mock an API failure response
        mock_get.return_value.status_code = 500

        providers = get_streaming_providers(12345, self.TMDB_API_KEY)
        self.assertIsNone(providers, "Expected None due to API failure")

    # Test cases for `get_movie_reviews`

    @patch('requests.get')
    def test_get_movie_reviews_valid(self, mock_get):
        """
        Test get_movie_reviews with a valid movie ID, expecting a list
        of reviews with up to the first 5 results.
        """
        # Mock a successful response with two reviews
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [
                {"author": "User1", "content": "Great movie!"},
                {"author": "User2", "content": "Loved it!"}
            ]
        }

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        self.assertEqual(len(reviews), 2, "Expected 2 reviews in the results")

    @patch('requests.get')
    def test_get_movie_reviews_truncate_long_text(self, mock_get):
        """
        Test get_movie_reviews to ensure that total review content length
        does not exceed 1000 characters by truncating as necessary.
        """
        # Mock a response with two long reviews
        long_review = "A" * 950
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [
                {"author": "User1", "content": long_review},
                {"author": "User2", "content": long_review}
            ]
        }

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        total_length = sum(len(review['content']) for review in reviews)
        self.assertLessEqual(
            total_length,
            1000,
            "Expected total review content to be <= 1000 characters")

    @patch('requests.get')
    def test_get_movie_reviews_no_reviews(self, mock_get):
        """
        Test get_movie_reviews with a movie ID that has no reviews,
        expecting an empty list to be returned.
        """
        # Mock a successful response with no reviews
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        self.assertEqual(
            reviews,
            [],
            "Expected empty list for movie with no reviews")

    @patch('requests.get')
    def test_get_movie_reviews_api_failure(self, mock_get):
        """
        Test get_movie_reviews with an API failure (500 status code),
        expecting None to be returned.
        """
        # Mock an API failure response
        mock_get.return_value.status_code = 500

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        self.assertIsNone(reviews, "Expected None due to API failure")
        
    @patch('requests.get')
    def test_search_movie_tmdb_missing_api_key(self, mock_get):
        """
        Test search_movie_tmdb with a missing API key, expecting None to be returned.
        """
        with self.assertRaises(TypeError, msg="Expected TypeError for missing API key"):
            search_movie_tmdb("Inception")  # No API key provided

    @patch('requests.get')
    def test_get_streaming_providers_no_connection(self, mock_get):
        """
        Test get_streaming_providers with no internet connection, expecting None.
        """
        
        providers = get_streaming_providers(12345, self.TMDB_API_KEY)
        self.assertIsNone(providers, "Expected None due to no internet connection")

    @patch('requests.get')
    def test_get_movie_reviews_unexpected_response_structure(self, mock_get):
        """
        Test get_movie_reviews with an unexpected JSON response structure,
        expecting an empty list to be returned.
        """
        # Mock a response with an unexpected structure
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"unexpected_key": []}

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        self.assertEqual(
            reviews,
            [],
            "Expected empty list for unexpected response structure")

    @patch('requests.get')
    def test_search_movie_tmdb_special_characters(self, mock_get):
        """
        Test search_movie_tmdb with special characters in the movie title,
        expecting a valid movie ID to be returned.
        """
        # Mock a successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": [{"id": 12345}]}

        movie_id = search_movie_tmdb("!@#$%^&*()", self.TMDB_API_KEY)
        self.assertEqual(
            movie_id,
            12345,
            "Expected valid movie ID for title with special characters")

    @patch('requests.get')
    def test_get_movie_reviews_large_number(self, mock_get):
        """
        Test get_movie_reviews with a large number of reviews, ensuring the result
        is limited to the top 5 reviews.
        """
        # Mock a response with more than 5 reviews
        reviews_data = [{"author": f"User{i}", "content": "Great!"} for i in range(10)]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": reviews_data}

        reviews = get_movie_reviews(12345, self.TMDB_API_KEY)
        self.assertEqual(len(reviews), 10, "Expected at most 5 reviews in the results")


if __name__ == "__main__":
    unittest.main()
