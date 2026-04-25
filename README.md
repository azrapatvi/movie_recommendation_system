# 🎬 Movie Recommendation System

A machine learning web app that recommends 5 movies similar to the one you pick — complete with **movie posters** fetched live from the internet! Built with **Streamlit** and powered by **Cosine Similarity**.

---

## 🌐 Live Demo Preview

> Select a movie → Click "Recommend" → See 5 similar movies with posters instantly!

---

## 📌 What Does This Project Do?

You **select a movie** from a dropdown (like **"Avatar"**), click the **Recommend** button, and the app shows you **5 similar movies** along with their **official posters** — all in a clean, side-by-side layout.

---

## 🧠 Types of Recommendation Systems (Theory)

| Type | How It Works | Used By |
|------|-------------|---------|
| **Content Based** | Recommends based on movie's own content (genre, cast, plot) | This Project ✅ |
| **Collaborative Based** | Recommends based on what similar users liked | Amazon |
| **Hybrid** | Combination of both | Netflix |

> 💡 This project uses **Content Based Filtering** — it looks at what's *inside* the movie (description, cast, director, genre, keywords) to find similar ones.

---

## 🗂️ Project Structure

```
movie-recommender/
│
├── app.py                               # 🌐 Main Streamlit Web App
│
├── movie_recommender.ipynb              # 🧪 Jupyter Notebook (ML model building)
│
├── joblib_files/
│   ├── movies.joblib                    # 💾 Saved movie dataframe
│   └── similarity_compressed.joblib    # 💾 Saved similarity matrix
│
├── tmdb_5000_movies.csv                 # 📊 Raw movie data
├── tmdb_5000_credits.csv                # 📊 Raw cast & crew data
│
└── README.md                            # 📖 This file
```

---

## ⚙️ How the ML Model Was Built (Inside the Notebook)

### Step 1: 📥 Load & Merge Data
Two datasets are loaded and merged into one big table using the movie `title` as the key:
```python
movies = movies.merge(credits, on='title')
```

---

### Step 2: 🧹 Keep Only Useful Columns
From the 20+ columns, only these 7 are kept:

| Column | Why It's Useful |
|--------|----------------|
| `movie_id` | To fetch posters from TMDB API |
| `title` | Movie name |
| `overview` | Plot summary |
| `genres` | Action, Drama, etc. |
| `keywords` | Important tags |
| `cast` | Top 3 actors |
| `crew` | Director only |

---

### Step 3: 🔄 Convert String Data to Real Lists
Raw data looks like this (a string pretending to be a list):
```
"[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]"
```
Using `ast.literal_eval()`, this is converted into a proper Python list:
```python
['Action', 'Adventure']
```

---

### Step 4: 🎭 Extract Key Info
- **Genres** → all genre names extracted
- **Keywords** → all keyword names extracted
- **Cast** → only **top 3 actors** (to keep it focused and avoid noise)
- **Crew** → only the **Director** extracted
- **Overview** → split into individual words

Spaces removed from names so they're treated as one word:
`"Sam Worthington"` → `"SamWorthington"`

---

### Step 5: 🏷️ Create a Combined "Tags" Column
Everything is merged into one text column called `tags`:

```python
tags = overview + genres + keywords + cast + crew
```

**Example for Avatar:**
```
"future humans travel pandora alien world battle resources jamescameron samworthington action adventure sciencefiction ..."
```

---

### Step 6: 🔡 Stemming (Root Word Conversion)
Using `PorterStemmer` from NLTK:

| Original Word | After Stemming |
|--------------|---------------|
| loved | love |
| loves | love |
| loving | love |
| running | run |

This helps match words even when they appear in different forms.

---

### Step 7: 🔢 Bag of Words — Text to Numbers
Using `CountVectorizer` from scikit-learn:
- Picks **top 5000 most frequent words** across all movies
- Removes useless filler words like "the", "is", "and" (stop words)
- Each movie becomes a **vector (list of numbers)**

**Result:** A matrix of shape `(4803 movies × 5000 words)`

---

### Step 8: 📐 Cosine Similarity
Measures how similar two movies are based on their word vectors:

- Score = **1** → Almost identical movies
- Score = **0** → Completely different movies

```python
similarity = cosine_similarity(vectors)
# Result: a 4803 × 4803 matrix
# Every movie is compared with every other movie
```

---

### Step 9: 💾 Save the Model with joblib
Both the dataframe and similarity matrix are saved so the web app doesn't recalculate everything from scratch every time:

```python
import joblib
joblib.dump(df, 'joblib_files/movies.joblib')
joblib.dump(similarity, 'joblib_files/similarity_compressed.joblib')
```

---

## 🌐 How the Web App Works (`app.py`)

### Step 1: 📦 Load Saved Model Files
```python
df = load('joblib_files/movies.joblib')
similarity = load('joblib_files/similarity_compressed.joblib')
```
Pre-built similarity data is loaded instantly — no need to recalculate!

---

### Step 2: 🖼️ Fetch Movie Posters from TMDB API
```python
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = session.get(url, timeout=10)
    data = response.json()
    poster_path = data.get("poster_path")
    return "https://image.tmdb.org/t/p/w500" + poster_path
```

- Uses the **TMDB (The Movie Database) API** to fetch official movie posters
- Each movie has a unique `movie_id` that is used to look it up
- If no poster is found → a placeholder image is shown instead
- Uses `requests.Session()` for faster repeated API calls (reuses the connection)
- `@st.cache_data` decorator means the poster is fetched **only once per movie** and cached in memory

---

### Step 3: 🎯 The `recommend()` Function
```python
def recommend(movie_name):
    movie_index = df[df['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    sorted_movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]  # Top 5, skip index 0 (the movie itself)

    for i in sorted_movie_list:
        names.append(df.iloc[i[0]].title)
        posters.append(fetch_poster(df.iloc[i[0]].movie_id))

    return names, posters
```

What it does step by step:
1. Finds the **row index** of the selected movie in the dataframe
2. Gets its **similarity scores** with all 4803 other movies
3. **Sorts** them from highest to lowest similarity
4. Skips `[0]` — that's the movie itself!
5. Takes the **next 5** most similar movies `[1:6]`
6. Fetches their **names and posters**
7. Returns both lists

---

### Step 4: 🖥️ The Streamlit UI
```python
st.title("🎬 Movie Recommendation System")
movie_name = st.selectbox('Select movie:', df['title'].values)

if st.button("Recommend"):
    with st.spinner("Loading posters..."):
        names, posters = recommend(movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.caption(names[i])
```

| Streamlit Component | What It Does |
|--------------------|-------------|
| `st.title()` | Shows the big heading at the top of the page |
| `st.selectbox()` | Dropdown menu with all 4803 movie titles |
| `st.button()` | The "Recommend" button |
| `st.spinner()` | Shows a loading animation while posters are being fetched |
| `st.columns(5)` | Creates 5 equal side-by-side columns |
| `st.image()` | Displays the movie poster image |
| `st.caption()` | Shows the movie title below each poster |

---

## 📊 Full Project Pipeline (Simple View)

```
Raw CSV Files (movies + credits)
           ↓
     Merge & Clean Data
           ↓
    Extract: Genre, Keywords,
         Cast, Director, Plot
           ↓
     Combine into "Tags"
           ↓
    Stemming (word → root form)
           ↓
  CountVectorizer (text → numbers)
           ↓
    Cosine Similarity Matrix
           ↓
       Save with joblib
           ↓
     Load in Streamlit App
           ↓
     User Selects a Movie
           ↓
   Find Top 5 Similar Movies
           ↓
    Fetch Posters from TMDB API
           ↓
    Show Results with Posters 🎬
```

---

## 🚀 How to Run This Project Locally

### 1. Clone / Download the Project
```bash
git clone https://github.com/your-username/movie-recommender.git
cd movie-recommender
```

### 2. Install Required Libraries
```bash
pip install streamlit pandas numpy scikit-learn nltk joblib requests
```

### 3. Run the Notebook First (to generate joblib files)
Open `movie_recommender.ipynb` in Jupyter or Google Colab and run all cells.

This will create:
- `joblib_files/movies.joblib`
- `joblib_files/similarity_compressed.joblib`

### 4. Run the Streamlit App
```bash
streamlit run app.py
```

### 5. Open in Browser
```
http://localhost:8501
```

---

## 🔑 TMDB API Key Setup

This project uses the **TMDB API** to fetch movie posters.

1. Go to [https://www.themoviedb.org/](https://www.themoviedb.org/) and create a free account
2. Go to **Settings → API** and generate your free API key
3. Replace the key in `app.py`:
```python
api_key = "your_api_key_here"
```

> ⚠️ Never share your real API key publicly — use environment variables in production!

---

## 📦 Libraries Used

| Library | Purpose |
|---------|---------|
| `streamlit` | Build the web app UI |
| `pandas` | Load and manipulate data |
| `numpy` | Numerical operations |
| `scikit-learn` | CountVectorizer + Cosine Similarity |
| `nltk` | PorterStemmer for stemming |
| `joblib` | Save and load the ML model files |
| `requests` | Call the TMDB API to get posters |

---

## 💡 Key Concepts Explained Simply

| Concept | Simple Explanation |
|---------|-------------------|
| **Stemming** | Cutting words to their root — "running" → "run" |
| **CountVectorizer** | Counts word occurrences and turns text into numbers |
| **Cosine Similarity** | Measures how "close" two movies are in terms of content |
| **Bag of Words** | Technique that counts words, ignoring their order |
| **joblib** | Like a "save file" for ML models — load it instantly later |
| **TMDB API** | Online database that provides official movie posters and info |
| **@st.cache_data** | Saves poster URLs in memory so they're not re-fetched every time |
| **requests.Session()** | Reuses internet connection for faster repeated API calls |
| **ast.literal_eval()** | Converts a string `"[1,2,3]"` into an actual Python list `[1,2,3]` |

---

## 📝 Notes

- Dataset contains **4803 movies**
- Only **top 3 actors** are used from the cast
- Only the **Director** is used from crew
- Model is **content-based** — no user ratings involved
- Posters are fetched **live** from the TMDB API using `movie_id`
- If a poster is unavailable, a **placeholder image** is shown
- The similarity matrix is **pre-computed and saved** — the app loads it instantly without recalculating
