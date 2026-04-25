import streamlit as st
from joblib import load
import requests
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Outfit:wght@300;400;500;600&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: #f5f3ef;
    color: #1a1a1a;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3.5rem 5rem 5rem; max-width: 1150px; }

/* ── Hero ── */
.hero-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 2.8rem;
    border-bottom: 1.5px solid #e0ddd8;
    padding-bottom: 1.4rem;
}
.hero-left h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    line-height: 1;
    letter-spacing: -0.03em;
}
.hero-left h1 span {
    font-style: italic;
    font-weight: 400;
    color: #e05c2a;
}
.hero-left p {
    margin: 0.4rem 0 0;
    font-size: 0.88rem;
    color: #9e9a94;
    font-weight: 300;
    letter-spacing: 0.03em;
}
.hero-right {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c4c0b9;
}

/* ── Widget label ── */
label[data-testid="stWidgetLabel"] p {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.13em !important;
    text-transform: uppercase !important;
    color: #9e9a94 !important;
    margin-bottom: 0.35rem !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #e0ddd8 !important;
    border-radius: 8px !important;
    color: #1a1a1a !important;
    font-size: 0.95rem !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #e05c2a !important;
    box-shadow: 0 0 0 3px rgba(224,92,42,0.12) !important;
}

/* ── Button ── */
.stButton > button {
    background: #1a1a1a !important;
    color: #f5f3ef !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2.2rem !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: background 0.2s ease, transform 0.1s ease !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    background: #e05c2a !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Results label ── */
.results-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #c4c0b9;
    margin: 2.2rem 0 1.1rem 0;
}
.results-label span {
    color: #e05c2a;
    font-style: italic;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.85rem;
    font-weight: 400;
}

/* ── Movie card ── */
.movie-card {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    background: #ffffff;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.movie-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.14);
}
.movie-card img {
    width: 100%;
    display: block;
}
.movie-title {
    margin-top: 0.6rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: #4a4744;
    line-height: 1.4;
    text-align: left;
}
.movie-num {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #e05c2a;
    background: rgba(224,92,42,0.10);
    border-radius: 4px;
    padding: 1px 6px;
    margin-bottom: 0.3rem;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p {
    color: #e05c2a !important;
    font-family: 'Outfit', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── API & session ─────────────────────────────────────────────────────────────
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

    names, posters = [], []
    for i in sorted_movie_list:
        idx = i[0]
        movie_id = df.iloc[idx].movie_id
        movie_n  = df.iloc[idx].title
        names.append(movie_n)
        posters.append(fetch_poster(movie_id) if movie_id and movie_id != 0
                       else "https://via.placeholder.com/500x750?text=No+Image")
    return names, posters


# ── Load data ─────────────────────────────────────────────────────────────────
df         = load('joblib_files/movies.joblib')
similarity = load('joblib_files/similarity_compressed.joblib')

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-left">
        <h1>Cine<span>Match</span></h1>
        <p>Find your next favourite film in seconds</p>
    </div>
    <div class="hero-right">Content-based · TMDB</div>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
col_select, col_btn, col_gap = st.columns([4, 1.4, 2.6])

with col_select:
    movie_name = st.selectbox("Choose a movie you love", df['title'].values)

with col_btn:
    st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
    go = st.button("Find Films")

# ── Results ───────────────────────────────────────────────────────────────────
if go:
    with st.spinner("Fetching recommendations…"):
        names, posters = recommend(movie_name)

    st.markdown(
        f'<p class="results-label">Picked for you · <span>{movie_name}</span></p>',
        unsafe_allow_html=True
    )

    cols = st.columns(5, gap="medium")
    for i in range(5):
        with cols[i]:
            st.markdown(
                f'''<div class="movie-card">
                        <img src="{posters[i]}" />
                    </div>
                    <div class="movie-num">0{i+1}</div>
                    <p class="movie-title">{names[i]}</p>''',
                unsafe_allow_html=True
            )
