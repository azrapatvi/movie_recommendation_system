# 🎬 Movie Recommender System

A beginner-friendly machine learning project that recommends movies similar to the one you like — just like Netflix or YouTube suggestions!

---

## 📌 What Does This Project Do?

You give it a movie name (like **"Avatar"**), and it gives you **5 similar movies** you might enjoy.

It does this by reading the movie's description, genres, cast, crew, and keywords — and finding other movies that are most similar.

---

## 🧠 Types of Recommendation Systems (Theory)

There are 3 main types of recommendation systems:

| Type | How It Works | Example |
|------|-------------|---------|
| **Content Based** | Recommends based on YOUR past behaviour / what you watched | "You watched Avatar, here are similar sci-fi movies" |
| **Collaborative Based** | Recommends based on what SIMILAR USERS liked | "People who liked Avatar also liked Interstellar" |
| **Hybrid** | Combination of both above | Used by **Netflix** |

> 💡 This project uses **Content Based Filtering**.

---

## 📂 Dataset Used

Two CSV files from the **TMDB 5000 Movies Dataset**:

- `tmdb_5000_movies.csv` → Movie details (budget, genre, overview, etc.)
- `tmdb_5000_credits.csv` → Cast and crew info

**Total: 4803 movies**

### 📋 Important Columns Used:
| Column | What It Means |
|--------|--------------|
| `genres` | Type of movie (Action, Drama, etc.) |
| `keywords` | Important tags related to the movie |
| `overview` | Short description/summary of the movie |
| `cast` | Top 3 actors in the movie |
| `crew` | Director of the movie |
| `movie_id` | Unique ID for each movie |
| `title` | Name of the movie (always in English) |

---

## ⚙️ How It Works — Step by Step

### Step 1: 📥 Load the Data
```python
credits = pd.read_csv('tmdb_5000_credits.csv')
movies = pd.read_csv('tmdb_5000_movies.csv')
```
Two files are loaded and then **merged together** using the movie `title` as the common link.

---

### Step 2: 🧹 Clean the Data
- Keep only the useful columns: `genres`, `movie_id`, `keywords`, `title`, `overview`, `cast`, `crew`
- Remove rows with **missing values**
- Remove **duplicate** rows

---

### Step 3: 🔄 Convert Weird Formats
The genres, keywords, cast, and crew columns look like this in raw form:
```
"[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]"
```
This is a **string that looks like a list** — so we use `ast.literal_eval()` to convert it into a real Python list.

Then we extract just the **names**:
```python
['Action', 'Adventure', 'ScienceFiction']
```

---

### Step 4: 🎭 Extract Key Information

- **Genres** → extract all genre names
- **Keywords** → extract all keyword names
- **Cast** → extract only **top 3 actors** (to keep it focused)
- **Crew** → extract only the **Director's name**
- **Overview** → split into individual words

Spaces are removed from names to avoid confusion:  
`"Sam Worthington"` → `"SamWorthington"` (so it's treated as one word)

---

### Step 5: 🏷️ Create a "Tags" Column
All the cleaned info is **combined into one big text column** called `tags`:

```
tags = overview + genres + keywords + cast + crew
```

**Example for Avatar:**
```
"future humans travel pandora alien world battle resources jamescameron samworthington action adventure sciencefiction ..."
```

---

### Step 6: 🔡 Text Processing

- Convert everything to **lowercase**
- Apply **Stemming** using `PorterStemmer` from NLTK:
  - Stemming reduces words to their root form
  - `"loved"`, `"loves"`, `"loving"` → all become `"love"`
  - This helps match similar words even if they are in different forms

---

### Step 7: 🔢 Convert Text to Numbers (Bag of Words)
Computers can't understand text — they need numbers!

We use **CountVectorizer** from scikit-learn:
- It picks the **top 5000 most common words** across all movies
- Removes common English stop words like "the", "is", "and"
- Each movie becomes a **list of numbers** (a vector) — one number per word, showing how many times that word appears

**Result:** A matrix of shape `(4803 movies × 5000 words)`

---

### Step 8: 📐 Calculate Similarity (Cosine Similarity)
Now we find **how similar any two movies are** using **Cosine Similarity**:

- Think of each movie as an arrow pointing in a certain direction in space
- Two movies pointing in the **same direction** → **very similar** (score close to `1`)
- Two movies pointing in **opposite directions** → **not similar** (score close to `0`)

```python
similarity = cosine_similarity(vectors)
```

This creates a `4803 × 4803` table — each movie compared with every other movie!

---

### Step 9: 🎯 The `recommend()` Function
```python
def recommend(movie):
    movie_index = df[df['title'] == movie].index[0]
    distances = similarity[movie_index]
    sorted_movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    for i in sorted_movie_list:
        print(df.iloc[i[0]]['title'])
```

**What it does:**
1. Find the index of the input movie
2. Get its similarity scores with all other movies
3. Sort them from most similar to least similar
4. Skip the first result (it's the movie itself!)
5. Print the **Top 5** most similar movies

---

## 🚀 How to Run This Project

### Requirements
```
pandas
numpy
scikit-learn
nltk
ast (built-in)
```

### Installation
```bash
pip install pandas numpy scikit-learn nltk
```

### Steps
1. Upload the two dataset ZIP files to your Colab:
   - `tmdb_5000_credits.csv.zip`
   - `tmdb_5000_movies.csv.zip`

2. Unzip them:
```python
!unzip tmdb_5000_credits.csv.zip
!unzip tmdb_5000_movies.csv.zip
```

3. Run all the cells in order

4. At the end, enter any movie title when prompted:
```
enter movie title: Avatar
```

### Example Output
```
Recommended Movies:

Aliens vs Predator: Requiem

Titan A.E.

Independence Day

Ender's Game

Guardians of the Galaxy
```

---

## 🗂️ Project Structure

```
movie_recommender/
│
├── movie_recommender.ipynb        # Main Jupyter Notebook
├── tmdb_5000_movies.csv           # Movie details dataset
├── tmdb_5000_credits.csv          # Cast & crew dataset
└── README.md                      # This file
```

---

## 📊 Summary of the ML Pipeline

```
Raw Data
   ↓
Merge & Clean
   ↓
Extract Genres, Keywords, Cast, Director
   ↓
Combine into Tags
   ↓
Stemming (word root form)
   ↓
CountVectorizer (text → numbers)
   ↓
Cosine Similarity (find similar movies)
   ↓
recommend("movie name") → Top 5 Similar Movies
```

---

## 💡 Key Concepts Explained Simply

| Concept | Simple Explanation |
|---------|-------------------|
| **Stemming** | Cutting words to their root — "running" → "run" |
| **CountVectorizer** | Counts how many times each word appears in a movie's tags |
| **Cosine Similarity** | Measures how "close" two movies are based on their word counts |
| **Bag of Words** | A technique where we just count words, ignoring their order |
| **ast.literal_eval()** | Converts a string `"[1,2,3]"` into an actual list `[1,2,3]` |

---

## 👨‍💻 Built With

- **Python** 🐍
- **Pandas** — data manipulation
- **NumPy** — numerical operations
- **Scikit-learn** — CountVectorizer & Cosine Similarity
- **NLTK** — stemming
- **Google Colab** — development environment

---

## 📝 Notes

- The dataset contains **4803 movies**
- Only the **top 3 actors** from each movie's cast are considered
- Only the **director** is taken from the crew
- The model is **content-based** — it does NOT consider user ratings or reviews
- This is a **beginner-level ML project** — great for learning NLP and recommendation systems!
