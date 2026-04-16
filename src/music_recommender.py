"""
music_recommender.py
────────────────────
Content-based music recommendation engine.

How it works:
  1. Filter songs whose audio features match the detected emotion
  2. Among matching songs, use cosine similarity to rank them
  3. Apply a genre boost for preferred genres
  4. Return top-N recommendations

Key audio features used:
  valence        → how happy / positive the song sounds
  energy         → how intense / active it feels
  acousticness   → acoustic vs electronic
  danceability   → rhythmic structure
  tempo          → speed (already normalised in preprocess)
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.preprocess import load_and_clean_music_data, MUSIC_FEATURES
from src.emotion_mapping import EMOTION_FEATURE_FILTERS, EMOTION_PREFERRED_GENRES

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(__file__))
CSV_PATH  = os.path.join(BASE_DIR, "data", "music_data.csv")

# Audio features we'll feed into cosine similarity
SIMILARITY_FEATURES = [
    "valence", "energy", "danceability",
    "acousticness", "instrumentalness", "tempo",
]

# ──────────────────────────────────────────────────────────────────────────────
# RECOMMENDER CLASS
# ──────────────────────────────────────────────────────────────────────────────
class MusicRecommender:
    """
    Content-based music recommender.

    Usage:
        recommender = MusicRecommender()
        songs = recommender.recommend("happy", n=10)
    """

    def __init__(self, csv_path: str = CSV_PATH):
        self.df       = load_and_clean_music_data(csv_path)
        self.scaler   = MinMaxScaler()
        self._prepare_feature_matrix()

    def _prepare_feature_matrix(self):
        """
        Build a normalised feature matrix for ALL songs.
        This is used to compute cosine similarity quickly.
        """
        # Only keep features that exist in the dataset
        self.feature_cols = [f for f in SIMILARITY_FEATURES
                              if f in self.df.columns]

        feature_data = self.df[self.feature_cols].fillna(0).values
        self.feature_matrix = self.scaler.fit_transform(feature_data)
        print(f"✅ Music feature matrix built: {self.feature_matrix.shape}")

    def recommend(self, emotion: str, n: int = 10) -> list[dict]:
        """
        Recommend songs for a given emotion.

        Args:
            emotion : Detected emotion string (e.g. "happy", "sad")
            n       : Number of songs to return

        Returns:
            List of dicts, each dict = one song's info
        """
        emotion = emotion.lower().strip()

        # ── Step 1: Filter by audio feature ranges ────────────────
        filtered_df = self._filter_by_emotion(emotion)

        # If very few songs pass the filter, relax it
        if len(filtered_df) < n * 2:
            print(f"  ⚠️  Only {len(filtered_df)} songs after strict filter."
                  "  Relaxing constraints …")
            filtered_df = self._filter_by_emotion(emotion, relax=True)

        # If still too few, use everything
        if len(filtered_df) < n:
            filtered_df = self.df.copy()

        # ── Step 2: Cosine similarity against emotion target ───────
        target_vector = self._build_target_vector(emotion)
        filtered_idx  = filtered_df.index.tolist()
        song_features = self.feature_matrix[filtered_idx]

        similarities  = cosine_similarity([target_vector], song_features)[0]

        # ── Step 3: Genre boost ────────────────────────────────────
        preferred = EMOTION_PREFERRED_GENRES.get(emotion, [])
        boost     = np.array([
            0.05 if row["genre"] in preferred else 0.0
            for _, row in filtered_df.iterrows()
        ])
        final_scores = similarities + boost

        # ── Step 4: Pick top-N ────────────────────────────────────
        top_n_local_idx = np.argsort(final_scores)[::-1][:n]
        top_rows = filtered_df.iloc[top_n_local_idx]

        # ── Step 5: Format output ─────────────────────────────────
        results = []
        for _, row in top_rows.iterrows():
            results.append({
                "name":       row.get("name",   "Unknown"),
                "artist":     row.get("artist", "Unknown"),
                "genre":      row.get("genre",  "Unknown"),
                "year":       int(row["year"]) if "year" in row and not pd.isna(row["year"]) else "N/A",
                "valence":    round(float(row.get("valence", 0)), 3),
                "energy":     round(float(row.get("energy",  0)), 3),
                "tempo":      round(float(row.get("tempo",   0)), 3),
                "preview_url": row.get("spotify_preview_url", ""),
                "spotify_id":  row.get("spotify_id", ""),
            })
        return results

    def _filter_by_emotion(self, emotion: str, relax: bool = False) -> pd.DataFrame:
        """
        Return a sub-DataFrame of songs whose audio features
        fall within the emotion's target ranges.

        If relax=True, expand each range by ±0.15 to catch more songs.
        """
        filters = EMOTION_FEATURE_FILTERS.get(emotion,
                  EMOTION_FEATURE_FILTERS["neutral"])
        mask = pd.Series([True] * len(self.df), index=self.df.index)

        for feature, (lo, hi) in filters.items():
            if feature not in self.df.columns:
                continue
            if relax:
                lo = max(0.0, lo - 0.15)
                hi = min(1.0 if hi <= 1.0 else hi + 50, hi + 0.15)
            mask &= (self.df[feature] >= lo) & (self.df[feature] <= hi)

        return self.df[mask].copy()

    def _build_target_vector(self, emotion: str) -> np.ndarray:
        """
        Build an 'ideal' feature vector for the given emotion.
        All filter values are already in 0-1 range (same as our
        normalised feature matrix), so we just return the midpoints.
        """
        filters = EMOTION_FEATURE_FILTERS.get(emotion,
                  EMOTION_FEATURE_FILTERS["neutral"])
        target = []
        for feat in self.feature_cols:
            if feat in filters:
                lo, hi = filters[feat]
                target.append((lo + hi) / 2.0)
            else:
                target.append(0.5)  # default midpoint

        # feature_matrix was scaled with MinMaxScaler too,
        # so transform the target the same way for correct similarity.
        target_array = np.array(target).reshape(1, -1)
        scaled = self.scaler.transform(target_array)[0]
        return scaled


# ──────────────────────────────────────────────────────────────────────────────
# QUICK DEMO
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    recommender = MusicRecommender()

    for emo in ["happy", "sad", "angry", "neutral"]:
        print(f"\n🎵 Songs for emotion: {emo.upper()}")
        songs = recommender.recommend(emo, n=5)
        for i, s in enumerate(songs, 1):
            print(f"  {i}. {s['name']} — {s['artist']} "
                  f"[{s['genre']}] val={s['valence']} energy={s['energy']}")
