# StreamR

# Version: 1.0.0
# Date Released: 2024-11-01
# Authors: Sravya Yepuri, Chirag Hegde, Melika Ahmadi Ranjbar

# Licensed under the MIT License.
# You may obtain a copy of the License at

#     https://opensource.org/licenses/MIT


import requests

# Search for a movie by name and year, return movie ID


def search_movie_tmdb(movie_name, API_KEY, year=None):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": movie_name
    }
    if year:
        params["year"] = year

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Failed to fetch data from TMDb API")
        return None

    search_data = response.json()
    if not search_data['results']:
        return None

    # Return the movie ID of the first result
    return search_data['results'][0]['id']

# Fetch streaming providers for a movie by ID


def get_streaming_providers(movie_id, API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    providers_data = response.json()

    # Extract US streaming providers (or another country if preferred)
    streaming_info = []
    if 'results' in providers_data and 'US' in providers_data['results']:
        for provider in providers_data['results']['US'].get('buy', []):
            platform_name = provider['provider_name']
            platform_logo = provider['logo_path']
            streaming_info.append(
                (platform_name, f"https://image.tmdb.org/t/p/w500{platform_logo}"))

    return streaming_info

# Fetch the top 10 reviews for a movie by ID


def get_movie_reviews(movie_id, API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {"api_key": API_KEY}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    reviews = response.json().get('results', [])
    results = reviews[:max(len(reviews), 5)]
    length = 0
    const = 1000
    show = []
    # Results max 1000 characters
    for each in results:
        if length + len(each["content"]) <= const:
            length += len(each["content"])
            show.append(each)
        else:
            break
    print(length)
    return show
