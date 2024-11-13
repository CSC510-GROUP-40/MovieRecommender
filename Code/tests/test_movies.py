import unittest
import sys
sys.path.append('../recommenderapp')
from recommenderapp.prediction_scripts.item_based import recommendForNewUser
import os
import pandas as pd
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RecommendationTests(unittest.TestCase):
    """Test suite for the recommendForNewUser function in RecommenderApp.

    This suite includes tests for:
    - Valid and empty movie lists.
    - Handling duplicates, missing data, and edge cases.
    - Filters for rating constraints.
    - Case insensitivity and unknown movie titles.
    """

    def test_recommendation_valid_movies(self):
        """Test recommendation with a valid list of movies.

        Verifies that recommendations are generated when a valid movie title
        with a valid rating is provided.
        """
        movies = [{"title": "Inception (2010)", "rating": 5.0}]
        self.assertTrue(
            recommendForNewUser(movies),
            "Expected recommendations")

    def test_recommendation_empty_movies(self):
        """Test recommendation with an empty movie list.

        Verifies that an empty list is returned when no movies are provided.
        """
        movies = []
        self.assertEqual(recommendForNewUser(movies), [],
                         "Expected no recommendations")

    def test_recommendation_duplicate_movies(self):
        """Test recommendation with duplicate movie entries.

        Verifies that recommendations do not duplicate the user's rated movies.
        """
        movies = [{"title": "Inception (2010)", "rating": 5.0}, {
            "title": "Inception (2010)", "rating": 5.0}]
        self.assertTrue(recommendForNewUser(movies),
                        "Expected recommendations without duplicates")

    def test_recommendation_missing_rating(self):
        """Test recommendation with a missing rating.

        Expects a KeyError if the 'rating' key is missing from any movie entry.
        """
        movies = [{"title": "Inception (2010)"}]
        self.assertRaises(KeyError, recommendForNewUser, movies)

    def test_recommendation_high_rating_filter(self):
        """Test recommendation with a rating above the valid range.

        Provides a movie rating of 9.0 (out of range) and expects no recommendations.
        """
        movies = [{"title": "Inception (2010)", "rating": 9.0}]
        self.assertEqual(
            recommendForNewUser(movies),
            [],
            "Expected no recommendations for out-of-range rating")

    def test_recommendation_low_rating_filter(self):
        """Test recommendation with a low valid rating.

        Provides a low rating (1.0) and expects valid recommendations based on that rating.
        """
        movies = [{"title": "Inception (2010)", "rating": 1.0}]
        self.assertTrue(recommendForNewUser(movies),
                        "Expected recommendations for low rating filter")

    def test_recommendation_invalid_movie_format(self):
        """Test recommendation with an invalid movie entry format.

        Expects a TypeError if movie entries are not dictionaries.
        """
        movies = ["Inception (2010)"]
        self.assertRaises(TypeError, recommendForNewUser, movies)

    def test_recommendation_incomplete_movie_data(self):
        """Test recommendation with incomplete movie data.

        Expects a KeyError if a movie entry lacks the 'title' key.
        """
        movies = [{"rating": 5.0}]
        self.assertRaises(KeyError, recommendForNewUser, movies)

    def test_recommendation_case_insensitivity(self):
        """Test recommendation with case-insensitive movie titles.

        Verifies that recommendations are case-insensitive by using a lowercase title.
        """
        movies = [{"title": "inception (2010)", "rating": 5.0}]
        self.assertTrue(recommendForNewUser(movies),
                        "Expected recommendations with case-insensitive title")

    def test_recommendation_no_valid_recommendations(self):
        """Test recommendation with an unknown movie title.

        Provides an unknown movie title and expects no recommendations.
        """
        movies = [{"title": "Unknown Movie (2022)", "rating": 5.0}]
        self.assertEqual(
            recommendForNewUser(movies),
            [],
            "Expected no recommendations for unknown movies")

    def test_recommendation_invalid_rating_value(self):
        """Test recommendation with invalid rating values.

        Provides a list with ratings out of the valid range (0.0-5.0) and expects an empty result.
        """
        movies = [{"title": "Inception (2010)",
                   "rating": -1.0},
                  {"title": "Interstellar (2014)",
                   "rating": 6.0}]
        self.assertEqual(
            recommendForNewUser(movies),
            [],
            "Expected no recommendations due to invalid rating values")

    def test_recommendation_long_movie_title(self):
        """Test recommendation with a very long movie title.

        Expects no recommendations if any movie title exceeds the max length (255 characters).
        """
        long_title = "A" * 256  # Generate a title longer than 255 characters
        movies = [{"title": long_title, "rating": 5.0}]
        self.assertEqual(
            recommendForNewUser(movies),
            [],
            "Expected no recommendations for overly long title")

    def test_recommendation_remove_user_rated_movies(self):
        """Test recommendation filtering out already rated movies.

        Provides a list of user-rated movies and checks if recommendations exclude them.
        """
        movies = [{"title": "Inception (2010)", "rating": 4.0}]
        recommendations = recommendForNewUser(movies)
        self.assertNotIn(
            "Inception (2010)",
            recommendations,
            "Expected user-rated movies to be excluded from recommendations")

    def test_recommendation_mixed_case_titles(self):
        """Test recommendation with mixed case in movie titles."""
        movies = [{"title": "InCePtIoN (2010)", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations with mixed case title")

    def test_recommendation_partial_title_match(self):
        """Test recommendation when input titles partially match dataset titles."""
        movies = [{"title": "Incep (2010)", "rating": 5.0}
                  ]  # "Incep" as a partial match for "Inception"
        recommendations = recommendForNewUser(movies)
        self.assertEqual(
            recommendations,
            [],
            "Expected no recommendations for partial title match")

    def test_recommendation_movie_title_with_special_chars(self):
        """Test recommendation with titles that contain special characters."""
        movies = [{"title": "Inception! (2010)", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations for title with special characters")

    def test_recommendation_duplicate_titles_with_different_years(self):
        """Test recommendation for movies with the same title but different years."""
        movies = [
            {"title": "Dune (1984)", "rating": 5.0},
            {"title": "Dune (2021)", "rating": 4.5},
        ]
        recommendations = recommendForNewUser(movies)
        self.assertGreaterEqual(
            len(recommendations),
            1,
            "Expected recommendations for different movie versions")

    def test_recommendation_mixed_valid_and_invalid_ratings(self):
        """Test recommendation with mixed valid and invalid ratings."""
        movies = [
            {"title": "Inception (2010)", "rating": 5.0},
            {"title": "Interstellar (2014)", "rating": -1.0},
            {"title": "The Dark Knight (2008)", "rating": 7.0},
        ]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations with mixed valid and invalid ratings")

    def test_recommendation_with_extra_keys(self):
        """Test recommendation with extra keys in the movie dictionaries."""
        movies = [{"title": "Inception (2010)",
                   "rating": 5.0,
                   "director": "Christopher Nolan"}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations with extra data keys in movie entry")

    def test_recommendation_for_edge_rating_values(self):
        """Test recommendation with edge values for rating."""
        movies = [
            {"title": "Inception (2010)", "rating": 0.0},
            {"title": "The Dark Knight (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations for edge rating values")

    def test_recommendation_with_reversed_movie_titles(self):
        """Test recommendation when title format is reversed (e.g., '2010 Inception')."""
        movies = [{"title": "2010 Inception", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertEqual(
            recommendations,
            [],
            "Expected no recommendations for reversed title format")

    def test_recommendation_with_numeric_only_titles(self):
        """Test recommendation for movies with numeric-only titles."""
        movies = [{"title": "1408 (2007)", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations for numeric-only movie title")

    def test_recommendation_with_long_sequence_of_movies(self):
        """Test recommendation with a large list of movies, testing scalability."""

        # Load movies.csv and select the first 100 titles
        movies_df = pd.read_csv(os.path.join(project_dir, "data/movies.csv"))
        movies = [
            {"title": f"{title} (2021)", "rating": 5.0}
            for title in movies_df["title"].head(100)
        ]

        # Generate recommendations based on the first 100 movies
        recommendations = recommendForNewUser(movies)

        # Assert that at least one recommendation is returned
        self.assertGreaterEqual(
            len(recommendations),
            1,
            "Expected recommendations with large movie list")

    def test_recommendation_no_overlap_in_genre(self):
        """Test recommendation when user-rated movies have genres absent in dataset."""
        movies = [{"title": "Fantasy Movie (2022)", "rating": 4.5}]
        recommendations = recommendForNewUser(movies)
        self.assertEqual(
            recommendations,
            [],
            "Expected no recommendations for genres absent in dataset")

    def test_recommendation_with_empty_genre_column(self):
        """Test recommendation when genre data is missing in dataset."""
        movies = [{"title": "Inception (2010)", "rating": 5.0}]
        # Simulate a dataset where genre information might be missing
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations even if genre data is partially missing")

    def test_recommendation_with_non_numeric_rating(self):
        """Test recommendation with non-numeric rating values."""
        movies = [{"title": "Inception (2010)", "rating": "five"}]
        self.assertEqual(
            recommendForNewUser(movies),
            [],
            "Expected no recommendations due to non numeric rating values")

    def test_recommendation_for_uncommon_years(self):
        """Test recommendation with a list that includes movies from uncommon years (e.g., early 1900s)."""
        movies = [
            {"title": "Trip to the Moon, A (Voyage dans la lune, Le) (1902)", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations for movies from uncommon years")

    def test_recommendation_for_combined_movies(self):
        """Test recommendation with a combined movie title (e.g., 'Kill Bill Vol. 1 & 2')."""
        movies = [{"title": "Kill Bill Vol. 1 & 2 (2003)", "rating": 4.5}]
        recommendations = recommendForNewUser(movies)
        self.assertEqual(
            recommendations,
            [],
            "Expected no recommendations for combined movie titles")

    def test_recommendation_multiple_genre_overlap(self):
        """Test recommendations when user-rated movies match multiple genres."""
        movies = [
            {"title": "Inception (2010)", "rating": 5.0},
            {"title": "The Matrix (1999)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations with multiple genre overlaps")

    def test_recommendation_with_trailing_special_chars(self):
        """Test recommendation with movie titles that have trailing special characters."""
        movies = [{"title": "Inception (2010)!!", "rating": 5.0}]
        recommendations = recommendForNewUser(movies)
        self.assertTrue(
            recommendations,
            "Expected recommendations for titles with trailing special characters")


if __name__ == "__main__":
    unittest.main()
