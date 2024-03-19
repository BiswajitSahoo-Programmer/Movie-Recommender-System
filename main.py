import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def fetch_poster(movie_id):
    api_key = 'YOUR_API_KEY'  # Replace 'YOUR_API_KEY' with your actual TMDb API key
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1  # Factor by which the sleep time is increased between retries
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    try:
        response = session.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6ee0b975fef62c3cfa7968ccbb2031a9&language=en-US')
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return None
    except requests.exceptions.RequestException as e:
        # Handle retry exhaustion or other errors
        print("Error fetching poster:", e)
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(poster_url)
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title('Movie Recommender System')

option = st.selectbox(
    'How would you like to be contracted?',
    movies['title'].values)
if st.button('Recommend'):
    names, posters = recommend(option)
    columns = st.columns(5)
    for i, (name, poster) in enumerate(zip(names, posters)):
        with columns[i]:
            st.text(name)
            st.image(poster)
