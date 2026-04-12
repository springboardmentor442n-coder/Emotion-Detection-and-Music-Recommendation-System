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

EMOTION_TAG_MAP = {
    'happy':    'upbeat pop dance energetic fun',
    'sad':      'melancholic slow acoustic ballad blues',
    'angry':    'metal intense hard rock aggressive',
    'fear':     'ambient dark suspense cinematic',
    'neutral':  'lo-fi chill instrumental background',
    'surprise': 'upbeat eclectic energetic mixed',
}

AUDIO_COLS = ['valence', 'energy', 'danceability', 'acousticness', 'instrumentalness']

IDEAL_AUDIO_PROFILES = {
    'happy':    [0.85, 0.80, 0.75, 0.10, 0.00],
    'sad':      [0.15, 0.20, 0.30, 0.85, 0.10],
    'angry':    [0.10, 0.95, 0.40, 0.05, 0.10],
    'fear':     [0.10, 0.30, 0.20, 0.60, 0.80],
    'neutral':  [0.50, 0.40, 0.50, 0.50, 0.40],
    'surprise': [0.70, 0.85, 0.60, 0.20, 0.10],
}

# ==========================================
# 2. DATA LOADING (Runs ONCE when server starts)
# ==========================================

CSV_PATH = os.path.join(os.path.dirname(__file__), 'Music_data.csv')

try:
    _music_df = pd.read_csv(CSV_PATH)
    
    _music_df['tags'] = _music_df['tags'].fillna('')
    _music_df['genre'] = _music_df['genre'].fillna('')
    _music_df['combined_features'] = _music_df['tags'] + " " + _music_df['genre']
    
    _tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(_music_df['combined_features'])
    
    for col in AUDIO_COLS:
        if col not in _music_df.columns:
            _music_df[col] = 0.5
        _music_df[col] = pd.to_numeric(_music_df[col], errors='coerce').fillna(0.5)
        
    _scaler = MinMaxScaler()
    _audio_matrix = _scaler.fit_transform(_music_df[AUDIO_COLS])
    
    print(f"Successfully loaded Music_data.csv with {_music_df.shape[0]} tracks (Hybrid Mode).")

except Exception as e:
    print(f"Warning: Could not load music dataset from {CSV_PATH}. Error: {e}")
    _music_df = None


# ==========================================
# 3. RECOMMENDATION ENGINE FUNCTION
# ==========================================

def get_recommendations(emotion: str, top_n: int = 5) -> list:
    """
    Core function called by the Flask API to get song recommendations.
    
    Args:
        emotion (str): One of the 6 MoodMate emotion classes (e.g., 'sad').
        top_n (int): Number of tracks to return to the frontend.
        
    Returns:
        List of dictionaries. Each dictionary is a song with its Spotify URL and details.
    """
    
    if _music_df is None:
        return [{"error": "Music dataset not found or failed to load."}]

    # ==================================
    # STEP A: Calculate Text Similarity
    # ==================================
    query_tags = EMOTION_TAG_MAP.get(emotion, '')
    query_vec_text = _tfidf_vectorizer.transform([query_tags])
    sim_text = cosine_similarity(query_vec_text, _tfidf_matrix).flatten()
    
    if sim_text.max() > 0:
        sim_text = sim_text / sim_text.max()
        
    # ==================================
    # STEP B: Calculate Audio Similarity
    # ==================================
    ideal_audio_array = IDEAL_AUDIO_PROFILES.get(emotion, [0.5]*5)
    query_audio = np.array(ideal_audio_array).reshape(1, -1)
    dist_audio = euclidean_distances(query_audio, _audio_matrix).flatten()
    sim_audio = 1 / (1 + dist_audio)
    
    if sim_audio.max() > 0:
        sim_audio = sim_audio / sim_audio.max()
        
    # ==================================
    # STEP C: Combine and Pick Winners
    # ==================================
    hybrid_scores = (sim_text * 0.4) + (sim_audio * 0.6)

    # ── FIX 1: Increased pool size from 300 → 1000 for more valid-preview candidates
    pool_size = min(1000, len(hybrid_scores))
    top_pool_indices = hybrid_scores.argsort()[-pool_size:][::-1]

    # ── FIX 2: Stricter URL validation — must start with 'http'
    valid_indices = [
        i for i in top_pool_indices
        if str(_music_df.iloc[i].get('spotify_preview_url', '')).strip().startswith('http')
    ]

    # ── FIX 3: No fallback to unfiltered pool — only return songs with valid previews
    if not valid_indices:
        return [{"error": "No songs with previews found for this mood."}]

    top_indices = np.random.choice(valid_indices, size=min(top_n, len(valid_indices)), replace=False)

    recommendations = []
    for idx in top_indices:
        track = _music_df.iloc[idx]
        recommendations.append({
            'track_id': str(track.get('track_id', '')),
            'name': str(track.get('name', 'Unknown Title')),
            'artist': str(track.get('artist', 'Unknown Artist')),
            'spotify_id': str(track.get('spotify_id', '')),
            'preview_url': str(track.get('spotify_preview_url', '')),
            'tags': str(track.get('tags', '')),
            'genre': str(track.get('genre', '')),
            'match_score': round(float(hybrid_scores[idx]), 3)
        })
        
    return recommendations


# ==========================================
# 4. LOCAL TESTING BLOCK
# ==========================================
if __name__ == "__main__":
    print("\n--- Testing MATCH mode for 'sad' ---")
    match_recs = get_recommendations('sad', top_n=3)
    for i, r in enumerate(match_recs, 1):
        print(f"{i}. {r['name']} by {r['artist']} (Score: {r['match_score']})")
        print(f"   Tags/Genre: {r['tags']} | {r['genre']}")