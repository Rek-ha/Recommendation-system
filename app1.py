import requests
import time
import pickle
import streamlit as st

MAX_RETRIES = 3
RETRY_DELAY = 1  # in seconds

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=e1a03ce20fa89b889ce1bdf53c13a322&language=en-US".format(movie_id)
    retries = 0
    while retries < MAX_RETRIES:
        try:
            data = requests.get(url)
            data.raise_for_status()  # Raise an error if the request was not successful
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except requests.exceptions.RequestException as e:
            print(f"Error fetching poster: {e}. Retrying...")
            retries += 1
            time.sleep(RETRY_DELAY)
    print("Max retries exceeded. Failed to fetch poster.")
    return None

def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster with retry logic
        movie_id = movies.iloc[i[0]].movie_id
        poster_path = fetch_poster(movie_id)
        if poster_path:
            recommended_movie_posters.append(poster_path)
            recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Load movie data and similarity scores
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

# Streamlit app
st.header('Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
    col1, col2, col3, col4, col5 = st.columns(5)
    for i in range(min(5, len(recommended_movie_names))):
        with locals()[f"col{i+1}"]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])
            