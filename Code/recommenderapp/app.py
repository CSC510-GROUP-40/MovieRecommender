# StreamR

# Version: 1.0.0
# Date Released: 2024-11-01
# Authors: Sravya Yepuri, Chirag Hegde, Melika Ahmadi Ranjbar

# Licensed under the MIT License.
# You may obtain a copy of the License at

#     https://opensource.org/licenses/MIT




import logging
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
import sys
import csv
import time
import requests
from datetime import datetime

import re
import pandas as pd
from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
# sys.path.append("../../")
from prediction_scripts.item_based import recommendForNewUser
from prediction_scripts.search import Search
from prediction_scripts.filter import Filter
from prediction_scripts.tmdb_utils import get_movie_reviews, get_streaming_providers, search_movie_tmdb
load_dotenv()
LOGGER = logging.getLogger(__name__)




app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID", None)
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET", None)
app.config['GOOGLE_DISCOVERY_URL'] = os.environ.get("GOOGLE_DISCOVERY_URL", None)
app.config['GOOGLE_SIGN_IN_REDIRECT_URI'] = os.environ.get("GOOGLE_SIGN_IN_REDIRECT_URI", None)


# OAuth Client Setup
oauthclient = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
app.oauthclient = oauthclient


CORS(app, resources={r"/*": {"origins": "*"}})

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def get_google_provider_cfg():
    '''
    get the google oauth provider url
    '''
    return requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    # Added field for favorite genres
    favorite_genres = db.Column(db.String(200), nullable=True)
    watchlist_count = db.Column(db.Integer, default=0)
    rec_movies_count = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    recommended_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Recommendation {self.movie_title}>'


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(250), nullable=False)
    imdb_rating = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Replace 'YOUR_API_KEY' with your actual OMDB API key
OMDB_API_KEY = 'b726fa05'
TMDB_API_KEY = "9f385440fe752884a4f5b8ea5b6839dd"


# Route for user profile
@app.route('/profile')
@login_required
def profile():
    watchlist_count = Watchlist.query.filter_by(
        user_id=current_user.id).count()
    rec_movies_count = Recommendation.query.filter_by(
        user_id=current_user.id).count()

    return render_template(
        'profile.html',
        watchlist_count=watchlist_count,
        rec_movies_count=rec_movies_count)

# Edit profile


@app.route("/edit_profile", methods=["POST"])
@login_required
def edit_profile():
    current_user.favorite_genres = request.form.get("favorite_genres")
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))

# Change password


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    new_password = request.form.get("new_password")

    # Check if the new password is empty and provide feedback without raising
    # an exception
    if not new_password:
        flash("Password cannot be empty!", "danger")
        return redirect(url_for('profile'))

    # Set the new password and save to the database
    current_user.set_password(new_password)
    db.session.commit()

    flash("Password changed successfully!", "success")
    return redirect(url_for('profile'))


@app.route("/")
def landing_page():
    if current_user.is_authenticated:
        return render_template("landing_page.html")
    else:
        return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            error = 'Username is already taken. Please choose a different one.'
        elif existing_email:
            error = 'Email is already registered. Please choose a different one.'
        else:
            # If username and email are not taken, proceed with registration
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Automatically log in the user after registration
            login_user(user)
            return redirect(url_for('landing_page'))

    return render_template('register.html', error=error)


@app.route("/login/callback", methods=['GET'])
def google_loign_callback():
    '''
    handle callback data from google oauth and login user
    '''

    try:
        # Get authorization code from url returned by google
        code = request.args.get("code")
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        LOGGER.info("something of me")
        token_url, headers, body = app.oauthclient.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(app.config['GOOGLE_CLIENT_ID'],
                  app.config['GOOGLE_CLIENT_SECRET'],
                  ),
        )

        app.oauthclient.parse_request_body_response(
            json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = app.oauthclient.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        LOGGER.error("okay of me to es")
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            user_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            username = userinfo_response.json()["given_name"]

            existing_user = User.query.filter_by(email=user_email).first()

            if existing_user:
                login_user(existing_user)
                return redirect(url_for('landing_page'))

            else:
                # If username and email are not taken, proceed with registration
                user = User(username=username, email=user_email)
                user.set_password("")
                db.session.add(user)
                db.session.commit()

                # Automatically log in the user after registration
                login_user(user)
                return redirect(url_for('landing_page'))

        else:
            LOGGER.info("email not verified")
            error = "User email not available or not verified by Google."  # , 400
        return render_template('login.html', error=error)
    except Exception as e:
        LOGGER.error(f"error occured {e}")
        return render_template('login.html', error="an error occured please try again later")






@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(
            username=username).first()  # 'user' is now defined here

        if user is None or not user.check_password(password):
            error = 'Invalid username or password'
        else:
            login_user(user)
            return redirect(url_for('landing_page'))

    # If we reach this point without returning, 'user' was not assigned due to a POST
    # Or there was an error in login, handle accordingly
    return render_template('login.html', error=error)



@app.route("/google-login")
def google_login():
    '''
    provides sign in with google
    '''
    # get the url to hit for google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # construct request for google login and specify the fields on the account
    request_uri = app.oauthclient.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=app.config['GOOGLE_SIGN_IN_REDIRECT_URI'],
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing_page'))

class Movie():
    def __init__(self, title, poster, rating, genres):
        self.title = title
        self.poster = poster
        self.rating = rating
        self.genres = genres
    
    def to_dict(self):
        return {
            "title": self.title,
            "poster": self.poster,
            "rating": self.rating,
            "genres": self.genres
        }

# TODO: Add pagination
# get page number as a parameter
# if page number is not provided, default to 1
# checking movies that having N/A values and then send the request to tmdb
# restruct the response data and modify the ajax code of html page
# platform is not needed in this post method
@app.route("/predict", methods=["POST"])
def predict():
    data = json.loads(request.data)  # contains movies
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        training_data.append(movie_with_rating)

    # Get recommendations
    recommendations = recommendForNewUser(training_data)
    filtered_recommendations = []

    # Process recommendations and only consider those with valid movie info
    i = 1
    print(f"Number of recommendations: {len(recommendations)}")
    for movie in recommendations:
        if i > 10:  # Limit to 10 valid recommendations
            break

        # Get movie information from OMDB or other source
        movie_info = get_movie_info(movie)
        if not movie_info:
            continue  # If no movie information, skip to the next
        movie = movie_info["Title"]

        # Check if the movie has valid IMDb rating, genre, and poster
        if movie_info['imdbRating'] != 'N/A' and movie_info['Genre'] != 'N/A' and movie_info['Poster'] != 'N/A':
            # Add valid recommendation to filtered recommendations
            filtered_recommendations.append(Movie(title=movie, 
                                                  poster=movie_info['Poster'], 
                                                  rating=movie_info['imdbRating'], 
                                                  genres=movie_info['Genre'])
                                            .to_dict())

            # Save the recommendation to the database
            new_recommendation = Recommendation(
                user_id=current_user.id, movie_title=movie)
            db.session.add(new_recommendation)

            # Increment the count of valid recommendations
            i += 1

    db.session.commit()

    # Return the filtered recommendations
    return {"recommendations": filtered_recommendations}


@app.route("/history")
@login_required
def history():
    recommendations = Recommendation.query.filter_by(
        user_id=current_user.id).all()
    if not recommendations:
        # Passing a flag to indicate no recommendations found
        return render_template('history.html', recommendations=[])
    return render_template('history.html', recommendations=recommendations)


def get_movie_info(title):
    year = title[len(title) - 5:len(title) - 1]
    title = format_title(title)

    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}&y={year}"
    print(url)

    response = requests.get(url)
    if response.status_code == 200:
        platforms = get_streaming_providers(title, TMDB_API_KEY)
        movie_id = search_movie_tmdb(title, TMDB_API_KEY)
        reviews = get_movie_reviews(movie_id, TMDB_API_KEY)

        reviews_list = []
        for review in reviews:
            reviews_list.append(
                {"author": review['author'], "content": review['content']})

        res = response.json()
        if res['Response'] == "True":
            res = res | {'Platforms': platforms, 'Reviews': reviews_list}
            return res
        else:
            return {
                'Title': title,
                'Platforms': "N/A",
                'Reviews': "N/A",
                'imdbRating': "N/A",
                'Genre': 'N/A',
                "Poster": "https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return {
            'Title': title,
            'Platforms': "N/A",
            'Reviews': "N/A",
            'imdbRating': "N/A",
            'Genre': 'N/A',
            "Poster": "https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}


def format_title(movie_title):
    # Remove the year from the movie_title
    movie_title = movie_title[0:len(movie_title) - 7]
    movie_title = re.sub(r'\(.*?\)', '', movie_title).strip()

    if ',' in movie_title:
        parts = movie_title.split(', ')
        if len(parts) == 2:
            movie_title = f"{parts[1]} {parts[0]}"

    movie_title = re.sub(r'[^a-zA-Z\s]', '', movie_title).strip()
    movie_title = movie_title.replace("%20", " ")
    return movie_title


@app.route("/search", methods=["POST"])
def search():
    term = request.form["q"]
    search = Search()
    filtered_dict = search.resultsTop10(term)
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp


# Initialize Filter instance
filter = Filter()

# Route to render the filtering page


@app.route("/filtering")
@login_required
def filtering():
    return render_template('filtering.html')

# Route to filter movies by rating


@app.route("/ratingfilter", methods=["POST"])
def ratingfilter():
    rating = float(request.form.get("rating"))

    if rating is None:
        return jsonify({"error": "Rating not provided"}), 400

    filtered_movies = filter.resultsTop10rate(rating)

    # Convert pandas Series or DataFrame results to a list
    filtered_movies_list = [movie.tolist() if isinstance(
        movie, pd.Series) else movie for movie in filtered_movies]

    if not filtered_movies_list:
        return jsonify({"error": "No movies found for the given rating"}), 404

    return jsonify({"filtered_movies": filtered_movies_list}), 200

# Route to filter movies by genre


@app.route("/genrefilter", methods=["POST"])
def genrefilter():
    # Expecting genres as a list from the form
    genres = request.form.getlist("genres")

    if not genres:
        return jsonify({"error": "No genres provided"}), 400

    filtered_movies = filter.resultsTop10(genres)

    if not filtered_movies:
        return jsonify({"error": "No movies found for the given genres"}), 404

    return jsonify({"filtered_movies": filtered_movies}), 200


@app.route('/watchlist')
@login_required
def view_watchlist():
    # Fetch the user's watchlist
    watchlist_movies = Watchlist.query.filter_by(user_id=current_user.id).all()

    # Check if the watchlist is empty
    if not watchlist_movies:
        flash("You have no movies in your watchlist.", "info")
        return render_template(
            'watchlist.html',
            watchlist=watchlist_movies,
            empty=True)

    return render_template(
        'watchlist.html',
        watchlist=watchlist_movies,
        empty=False)


@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    movie_title = request.form.get('movie_title')
    imdb_rating = request.form.get('imdb_rating')

    # Check if the movie is already in the user's watchlist
    existing_movie = Watchlist.query.filter_by(
        user_id=current_user.id, movie_title=movie_title).first()
    if existing_movie:
        flash('Movie is already in your watchlist!', 'warning')
        return redirect(url_for('view_watchlist'))

    # Add the movie to the user's watchlist
    new_movie = Watchlist(
        movie_title=movie_title,
        imdb_rating=imdb_rating,
        user_id=current_user.id)
    db.session.add(new_movie)
    db.session.commit()

    flash('Movie added to your watchlist!', 'success')
    return redirect(url_for('view_watchlist'))


@app.route('/remove_from_watchlist/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    movie = Watchlist.query.get_or_404(movie_id)

    # Ensure the movie belongs to the current user
    if movie.user_id != current_user.id:
        flash('You do not have permission to remove this movie!', 'danger')
        return redirect(url_for('view_watchlist'))

    db.session.delete(movie)
    db.session.commit()

    flash('Movie removed from your watchlist.', 'success')
    return redirect(url_for('view_watchlist'))


@app.route("/feedback", methods=["POST"])
def feedback():
    data = json.loads(request.data)
    with open(f"experiment_results/feedback_{int(time.time())}.csv", "w") as f:
        for key in data.keys():
            f.write(f"{key} - {data[key]}\n")
    return data


@app.route('/get_reviews/<movie_title>', methods=['GET'])
def get_reviews(movie_title):
    movie_title = format_title(movie_title)
    movie_id = search_movie_tmdb(movie_title, TMDB_API_KEY)

    if movie_id:
        reviews = get_movie_reviews(movie_id, TMDB_API_KEY)
        reviews_list = [{"author": review['author'],
                         "content": review['content']} for review in reviews]
        return jsonify({"reviews": reviews_list})
    else:
        return jsonify({"reviews": []}), 404


@app.route('/get_streaming_platforms/<movie_title>', methods=['GET'])
def get_streaming_platforms(movie_title):
    year = movie_title[len(movie_title) - 5:len(movie_title) - 1]
    movie_title = format_title(movie_title)
    movie_id = search_movie_tmdb(movie_title, TMDB_API_KEY, year)

    if not movie_id:
        return jsonify([])  # No movie found

    streaming_info = get_streaming_providers(movie_id, TMDB_API_KEY)
    if streaming_info:
        return jsonify([{"name": platform_name, "logo": platform_logo}
                       for platform_name, platform_logo in streaming_info])
    else:
        return jsonify([])  # No streaming info found


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
