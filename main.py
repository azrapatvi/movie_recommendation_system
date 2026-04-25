import streamlit as st
from joblib import load
import requests
import time

api_key = "a6a617ebb6f117bffd65d4781c88eac2"


session = requests.Session()

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={api_key}"
    

    try:
        response = session.get(url, timeout=10)
        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except:
        time.sleep(0.3)

    return "https://via.placeholder.com/500x750?text=No+Image"


def recommend(movie_name):
    movie_index = df[df['title'] == movie_name].index[0]
    distances = similarity[movie_index]

    sorted_movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in sorted_movie_list:
        idx = i[0]

        movie_id = df.iloc[idx].movie_id
        movie_n = df.iloc[idx].title

        names.append(movie_n)

        if movie_id and movie_id != 0:
            posters.append(fetch_poster(movie_id))
        else:
            posters.append("https://via.placeholder.com/500x750?text=No+Image")

    return names, posters


# UI
st.title("🎬 Movie Recommendation System")

df = load('joblib_files/movies.joblib')
similarity = load('joblib_files/similarity_compressed.joblib')

movie_name = st.selectbox('Select movie:', df['title'].values)

if st.button("Recommend"):
    with st.spinner("Loading posters..."):
        names, posters = recommend(movie_name)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            
            st.image(posters[i])
            st.caption(names[i])
            