"""
Music recommendation engine for MoodMate.

Uses a hybrid approach:
1. Text Similarity: TF-IDF (Text Frequency) + Cosine Similarity on text (tags & genres)
2. Audio Similarity: Euclidean Distance Similarity on Spotify audio features (danceability, valence, etc.)
"""
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

# ==========================================
# 1. MAPPINGS & CONFIGURATION
# ==========================================

# We map each of MoodMate's 6 recognized emotions to a list of descriptive music tags.
# This text is used by the TF-IDF vectorizer to find songs with matching 'tags' or 'genre' text.
EMOTION_TAG_MAP = {
    'happy':    'upbeat pop dance energetic fun',
    'sad':      'melancholic slow acoustic ballad blues',
    'angry':    'metal intense hard rock aggressive',
    'fear':     'ambient dark suspense cinematic',
    'neutral':  'lo-fi chill instrumental background',
    'surprise': 'upbeat eclectic energetic mixed',
}

# When the user selects "uplift" mode, we intercept their negative emotion
# and change the target to a positive one.
UPLIFT_MAP = {
    'sad': 'happy',         # Uplift sadness to happiness
    'angry': 'neutral',     # Calm anger down to a neutral chill state
    'fear': 'happy',        # Shift fear to an upbeat/fun state
    'neutral': 'happy',     # Make neutral more energetic
    'happy': 'happy',       # If they are already happy, keep them happy
    'surprise': 'surprise'  # If they are surprised, keep it surprisingly positive
}

# These are the exact numerical Spotify Audio Features we care about from the CSV dataset.
AUDIO_COLS = ['valence', 'energy', 'danceability', 'acousticness', 'instrumentalness']

# This is the secret sauce: For each emotion, what is the *perfect* score (from 0.0 to 1.0)
# for the 5 Spotify audio features listed above? 
# [valence (happiness), energy, danceability, acousticness, instrumentalness]
IDEAL_AUDIO_PROFILES = {
    'happy':    [0.85, 0.80, 0.75, 0.10, 0.00], # Very happy, very energetic, very danceable
    'sad':      [0.15, 0.20, 0.30, 0.85, 0.10], # Very sad, very low energy, highly acoustic (like a solo guitar/piano)
    'angry':    [0.10, 0.95, 0.40, 0.05, 0.10], # Very unhappy, but EXTREMELY high energy (like heavy metal)
    'fear':     [0.10, 0.30, 0.20, 0.60, 0.80], # Unhappy, low energy, highly instrumental (like a scary movie soundtrack)
    'neutral':  [0.50, 0.40, 0.50, 0.50, 0.40], # Exact middle of the road for everything (chill, lo-fi)
    'surprise': [0.70, 0.85, 0.60, 0.20, 0.10], # Energetic, positive, fast
}

# ==========================================
# 2. DATA LOADING (Runs ONCE when server starts)
# ==========================================

# We construct the absolute path to Music_data.csv located in the same folder as this script.
CSV_PATH = os.path.join(os.path.dirname(__file__), 'Music_data.csv')

try:
    # Load the 50,000+ row CSV into a Pandas DataFrame for lightning-fast memory access
    _music_df = pd.read_csv(CSV_PATH)
    
    # --- TEXT FEATURES SETUP ---
    # Replace any empty missing values in 'tags' and 'genre' with blank strings to prevent crashes
    _music_df['tags'] = _music_df['tags'].fillna('')
    _music_df['genre'] = _music_df['genre'].fillna('')
    
    # Mash the tags and genre together into one giant text column per song so we can search it easily
    _music_df['combined_features'] = _music_df['tags'] + " " + _music_df['genre']
    
    # Create the TF-IDF Vectorizer. This turns text (like "pop dance") into a grid of math numbers.
    # stop_words='english' removes useless words like "the", "and", "or".
    _tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    # Pre-calculate the text math grid for all 50k songs instantly 
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(_music_df['combined_features'])
    
    # --- AUDIO FEATURES SETUP ---
    # Ensure all 5 of our target audio columns exist. If a song is completely missing info, default to 0.5 (neutral).
    for col in AUDIO_COLS:
        if col not in _music_df.columns:
            _music_df[col] = 0.5
        # pd.to_numeric forces the column to be numbers. 'coerce' turns bad data into NaN, which we then fill with 0.5
        _music_df[col] = pd.to_numeric(_music_df[col], errors='coerce').fillna(0.5)
        
    # MinMaxScaler strictly forces all audio data values to exactly fit between 0.0 and 1.0
    # This prevents 'tempo' (which can be 200) from overpowering 'valence' (which is only 1.0).
    _scaler = MinMaxScaler()
    _audio_matrix = _scaler.fit_transform(_music_df[AUDIO_COLS])
    
    print(f"Successfully loaded Music_data.csv with {_music_df.shape[0]} tracks (Hybrid Mode).")

except Exception as e:
    # If the CSV is missing or corrupted, catch the error safely so Django doesn't crash
    print(f"Warning: Could not load music dataset from {CSV_PATH}. Error: {e}")
    _music_df = None


# ==========================================
# 3. RECOMMENDATION ENGINE FUNCTION
# ==========================================

def get_recommendations(emotion: str, mode: str = 'match', top_n: int = 5) -> list:
    """
    Core function called by the Django API to get song recommendations.
    
    Args:
        emotion (str): One of the 6 MoodMate emotion classes (e.g., 'sad').
        mode (str): 'match' (matches the exact emotion) or 'uplift' (cheers them up).
        top_n (int): Number of tracks to return to the frontend.
        
    Returns:
        List of dictionaries. Each dictionary is a song with its Spotify URL and details.
    """
    
    # Safety Check: If data didn't load properly at startup, return an error message
    if _music_df is None:
        return [{"error": "Music dataset not found or failed to load."}]
        
    # --- Determine Target Emotion ---
    target_emotion = emotion
    if mode == 'uplift':
        # If user wants to be uplifted, look up the target emotion (e.g., 'sad' becomes 'happy')
        target_emotion = UPLIFT_MAP.get(emotion, emotion)
        
    # ==================================
    # STEP A: Calculate Text Similarity
    # ==================================
    # 1. Get the ideal text string describing this emotion (e.g., "upbeat pop dance")
    query_tags = EMOTION_TAG_MAP.get(target_emotion, '')
    
    # 2. Turn that single string into a math vector
    query_vec_text = _tfidf_vectorizer.transform([query_tags])
    
    # 3. Compare our 1 query vector against all 50,000 pre-calculated song vectors
    # Cosine similarity returns 1.0 if perfectly matched, 0.0 if entirely different.
    sim_text = cosine_similarity(query_vec_text, _tfidf_matrix).flatten()
    
    # 4. Normalize the results so the highest text match is exactly 1.0
    if sim_text.max() > 0:
        sim_text = sim_text / sim_text.max()
        
    # ==================================
    # STEP B: Calculate Audio Similarity
    # ==================================
    # 1. Fetch the ideal [valence, energy, dance, acoustic, instrumental] profile array
    ideal_audio_array = IDEAL_AUDIO_PROFILES.get(target_emotion, [0.5]*5)
    
    # 2. Convert it into a Numpy row vector so Scikit-Learn can understand it
    query_audio = np.array(ideal_audio_array).reshape(1, -1)
    
    # 3. Calculate "Euclidean Distance". This measures how physically far apart our ideal numbers
    # are from every song's actual numbers. A distance of 0 means a perfect match.
    dist_audio = euclidean_distances(query_audio, _audio_matrix).flatten()
    
    # 4. Convert Distance into Similarity. 
    # If distance is 0, (1 / 1+0) = 1.0 (High Similarity). 
    # If distance is high, (1 / 1+High) = 0.01 (Low Similarity).
    sim_audio = 1 / (1 + dist_audio)
    
    # 5. Normalize the results so the highest physical audio match is exactly 1.0
    if sim_audio.max() > 0:
        sim_audio = sim_audio / sim_audio.max()
        
    # ==================================
    # STEP C: Combine and Pick Winners
    # ==================================
    # Hybrid Scoring: We want the Spotify audio features to matter slightly more (60%) 
    # than just matching random text tags (40%), ensuring the song actually *sounds* right.
    hybrid_scores = (sim_text * 0.4) + (sim_audio * 0.6)
    
    # Grab a larger pool of the best matches (top 300) to introduce high variety
    pool_size = min(300, len(hybrid_scores))
    top_pool_indices = hybrid_scores.argsort()[-pool_size:][::-1]
    
    # Randomly select 'top_n' tracks from that high-quality pool
    top_indices = np.random.choice(top_pool_indices, size=min(top_n, pool_size), replace=False)
    
    recommendations = []
    
    # Loop through the winning indices to build the final list of dictionaries
    for idx in top_indices:
        track = _music_df.iloc[idx] # Grab the song's row from the Pandas DataFrame
        
        # Package the row data into JSON-friendly format for the React Frontend
        recommendations.append({
            'track_id': str(track.get('track_id', '')),
            'name': str(track.get('name', 'Unknown Title')),
            'artist': str(track.get('artist', 'Unknown Artist')),
            'spotify_id': str(track.get('spotify_id', '')),
            'preview_url': str(track.get('spotify_preview_url', '')),
            'tags': str(track.get('tags', '')),
            'genre': str(track.get('genre', '')),
            # Keep the match score limited to 3 decimal places for readability
            'match_score': round(float(hybrid_scores[idx]), 3) 
        })
        
    return recommendations
    

# ==========================================
# 4. LOCAL TESTING BLOCK
# ==========================================
# Code inside this block ONLY runs if you type `python recommender.py` in the terminal.
# It gets ignored entirely when Django imports this file later.
if __name__ == "__main__":
    print("\n--- Testing MATCH mode for 'sad' (Hybrid Audio+Text) ---")
    # We ask for the top 3 tracks for sadness
    match_recs = get_recommendations('sad', mode='match', top_n=3)
    for i, r in enumerate(match_recs, 1):
        print(f"{i}. {r['name']} by {r['artist']} (Score: {r['match_score']})")
        print(f"   Tags/Genre: {r['tags']} | {r['genre']}")
        
    print("\n--- Testing UPLIFT mode for 'sad' (Should leap to high valence/energy) ---")
    # We ask to be uplifted from sadness
    uplift_recs = get_recommendations('sad', mode='uplift', top_n=3)
    for i, r in enumerate(uplift_recs, 1):
        print(f"{i}. {r['name']} by {r['artist']} (Score: {r['match_score']})")
        print(f"   Tags/Genre: {r['tags']} | {r['genre']}")
