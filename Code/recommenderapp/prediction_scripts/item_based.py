# StreamR

# Version: 1.0.0
# Date Released: 2024-11-01
# Authors: Sravya Yepuri, Chirag Hegde, Melika Ahmadi Ranjbar

# Licensed under the MIT License.
# You may obtain a copy of the License at

#     https://opensource.org/licenses/MIT

import pandas as pd
import warnings
import os
import re
import unidecode

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

warnings.filterwarnings("ignore")


def recommendForNewUser(user_rating):
    if not user_rating:
        return []

    # Process valid ratings only, filter out invalid ones
    valid_user_ratings = [rating for rating in user_rating if isinstance(
        rating["rating"], (int, float)) and 0.0 <= rating["rating"] <= 5.0]
    if not valid_user_ratings:
        return []

    # Load ratings and movies data
    ratings = pd.read_csv(project_dir + "/recommenderapp/prediction_scripts/data/ratings.csv")
    movies = pd.read_csv(project_dir + "/recommenderapp/prediction_scripts/data/movies.csv")

    user = pd.DataFrame(valid_user_ratings)

    # Standardize titles in user and movies data
    def standardize_title(title):
        title = title.strip().lower()
        # Retain primary title and year only
        title = re.sub(r'(\(\d{4}\)).*', r'\1', title)
        # Remove special chars and accents
        title = re.sub(r'[^a-zA-Z0-9\s\(\)]', '', unidecode.unidecode(title))
        title = re.sub(r'\s+', ' ', title)  # Normalize spaces
        return title

    # Apply standardization to both user-provided titles and movie titles
    user["title"] = user["title"].apply(
        lambda x: standardize_title(x) if isinstance(
            x, str) else x)
    movies["title"] = movies["title"].apply(
        lambda x: standardize_title(x) if isinstance(
            x, str) else x)

    # Drop duplicates in user DataFrame after standardization
    user = user.drop_duplicates(subset=["title"])

    # Merge user ratings with movies based on standardized titles
    userMovieID = movies[movies["title"].isin(user["title"])]
    userRatings = pd.merge(userMovieID, user)

    # Check for too long movie titles
    max_title_length = 255  # Set your desired maximum title length
    if any(len(title) > max_title_length for title in user["title"]):
        return []  # Return an empty list if any title is too long

     # Ensure that the "title" key exists in each rating dictionary
    user = user[user["title"].isin(
        movies["title"])] if "title" in user.columns else pd.DataFrame()
    if user.empty:
        return []  # Return an empty list if no valid movie titles are found in the input

    moviesGenreFilled = movies.copy(deep=True)
    copyOfMovies = movies.copy(deep=True)
    for index, row in copyOfMovies.iterrows():
        copyOfMovies.at[index, "genres"] = row["genres"].split("|")
    for index, row in copyOfMovies.iterrows():
        for genre in row["genres"]:
            moviesGenreFilled.at[index, genre] = 1
    moviesGenreFilled = moviesGenreFilled.fillna(0)

    userGenre = moviesGenreFilled[moviesGenreFilled.movieId.isin(
        userRatings.movieId)]
    userGenre.drop(["movieId", "title", "genres"], axis=1, inplace=True)
    userProfile = userGenre.T.dot(userRatings.rating.to_numpy())

    # Normalize genres in movies and calculate recommendations
    moviesGenreFilled.set_index(moviesGenreFilled.movieId)
    moviesGenreFilled.drop(
        ["movieId", "title", "genres"], axis=1, inplace=True)

    recommendations = (moviesGenreFilled.dot(userProfile)) / userProfile.sum()

    # Join recommendations with movies and sort
    joinMoviesAndRecommendations = movies.copy()
    joinMoviesAndRecommendations["recommended"] = recommendations
    joinMoviesAndRecommendations.sort_values(
        by="recommended", ascending=False, inplace=True)

    # Remove the movies that the user has already rated (training data)
    # Movies in training data
    rated_movie_titles = userRatings["title"].tolist()
    joinMoviesAndRecommendations = joinMoviesAndRecommendations[~joinMoviesAndRecommendations["title"].isin(
        rated_movie_titles)]

    return [x for x in joinMoviesAndRecommendations["title"]][:201]
