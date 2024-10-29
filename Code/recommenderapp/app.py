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
from tmdb_utils import get_movie_reviews, get_streaming_providers, search_movie_tmdb
import re
import pandas as pd

sys.path.append("../../")
from Code.prediction_scripts.item_based import recommendForNewUser
from search import Search
from filter import Filter

app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
CORS(app, resources={r"/*": {"origins": "*"}})

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    favorite_genres = db.Column(db.String(200), nullable=True)  # Added field for favorite genres
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
    watchlist_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    rec_movies_count = Recommendation.query.filter_by(user_id=current_user.id).count()
    
    return render_template('profile.html', watchlist_count=watchlist_count, rec_movies_count=rec_movies_count)

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
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for('profile'))

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
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()  # 'user' is now defined here

        if user is None or not user.check_password(password):
            error = 'Invalid username or password'
        else:
            login_user(user)
            return redirect(url_for('landing_page'))

    # If we reach this point without returning, 'user' was not assigned due to a POST
    # Or there was an error in login, handle accordingly
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing_page'))


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
    movie_with_rating = {}
    
    # Process recommendations and only consider those with valid movie info
    i = 1
    for movie in recommendations:
        if i > 10:  # Limit to 10 valid recommendations
            break
        
        # Get movie information from OMDB or other source
        movie_info = get_movie_info(movie)
        if not movie_info:
            continue  # If no movie information, skip to the next
        
        # Check if the movie has valid IMDb rating, genre, and poster
        if movie_info['imdbRating'] != 'N/A' and movie_info['Genre'] != 'N/A' and movie_info['Poster'] != 'N/A':
            movie_with_rating[movie+"-c"]=movie_info['Reviews']
            movie_with_rating[movie+"-s"]=movie_info['Platforms']
            movie_with_rating[movie + "-r"] = movie_info['imdbRating']
            movie_with_rating[movie + "-g"] = movie_info['Genre']
            movie_with_rating[movie + "-p"] = movie_info['Poster']
            
            # Add valid recommendation to filtered recommendations
            filtered_recommendations.append(movie)
            
            # Save the recommendation to the database
            new_recommendation = Recommendation(user_id=current_user.id, movie_title=movie)
            db.session.add(new_recommendation)
            
            # Increment the count of valid recommendations
            i += 1

    db.session.commit()

    resp = {"recommendations": filtered_recommendations, "rating":movie_with_rating}
    return resp

@app.route("/history")
@login_required
def history():
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', recommendations=recommendations)

def get_movie_info(title):
    year = title[len(title)-5:len(title)-1]
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
            reviews_list.append({"author": review['author'], "content": review['content']})
    
        res = response.json()
        if res['Response'] == "True":
            res = res | {'Platforms': platforms, 'Reviews': reviews_list}
            return res
        else:  
            return { 'Title': title, 'Platforms': "N/A", 'Reviews': "N/A", 'imdbRating':"N/A", 'Genre':'N/A',"Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return  { 'Title': title, 'Platforms': "N/A", 'Reviews': "N/A", 'imdbRating':"N/A",'Genre':'N/A', "Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}

def format_title(movie_title):
    movie_title = movie_title[0:len(movie_title)-7]  # Remove the year from the movie_title
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
    filtered_movies_list = [movie.tolist() if isinstance(movie, pd.Series) else movie for movie in filtered_movies]
    
    if not filtered_movies_list:
        return jsonify({"error": "No movies found for the given rating"}), 404
    
    return jsonify({"filtered_movies": filtered_movies_list}), 200

# Route to filter movies by genre
@app.route("/genrefilter", methods=["POST"])
def genrefilter():
    genres = request.form.getlist("genres")  # Expecting genres as a list from the form
    
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
        return render_template('watchlist.html', watchlist=watchlist_movies, empty=True)
    
    return render_template('watchlist.html', watchlist=watchlist_movies, empty=False)

@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    movie_title = request.form.get('movie_title')
    imdb_rating = request.form.get('imdb_rating')
    
    # Check if the movie is already in the user's watchlist
    existing_movie = Watchlist.query.filter_by(user_id=current_user.id, movie_title=movie_title).first()
    if existing_movie:
        flash('Movie is already in your watchlist!', 'warning')
        return redirect(url_for('view_watchlist'))
    
    # Add the movie to the user's watchlist
    new_movie = Watchlist(movie_title=movie_title, imdb_rating=imdb_rating, user_id=current_user.id)
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
        reviews_list = [{"author": review['author'], "content": review['content']} for review in reviews]
        return jsonify({"reviews": reviews_list})
    else:
        return jsonify({"reviews": []}), 404


@app.route('/get_streaming_platforms/<movie_title>', methods=['GET'])
def get_streaming_platforms(movie_title):
    year = movie_title[len(movie_title)-5:len(movie_title)-1]
    movie_title = format_title(movie_title)
    movie_id = search_movie_tmdb(movie_title, TMDB_API_KEY, year)
    
    if not movie_id:
        return jsonify([])  # No movie found
    
    streaming_info = get_streaming_providers(movie_id, TMDB_API_KEY)
    if streaming_info:
        return jsonify([{"name": platform_name, "logo": platform_logo} for platform_name, platform_logo in streaming_info])
    else:
        return jsonify([])  # No streaming info found


@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
