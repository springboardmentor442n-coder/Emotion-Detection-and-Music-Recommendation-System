from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..services.music_preview_service import get_song_preview_url


class MusicRecommender:
    def __init__(self, songs_csv_path: Path, emotion_map_path: Path) -> None:
        self.df = pd.read_csv(songs_csv_path)
        with open(emotion_map_path, "r", encoding="utf-8") as f:
            self.emotion_map = json.load(f)

        self.df["content"] = (self.df["genre"].fillna("") + " " + self.df["tags"].fillna("")).str.strip()
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.song_matrix = self.vectorizer.fit_transform(self.df["content"])

    def recommend(self, emotion: str, top_k: int = 5, randomize: bool = True) -> list[dict[str, Any]]:
        """Recommend songs for an emotion.
        
        Args:
            emotion: The detected emotion
            top_k: Number of songs to return
            randomize: If True, sample from top candidates with probability weights.
        """
        alias_map = {
            "happy": "joy",
            "sad": "sadness",
            "angry": "anger",
            "fearful": "fear",
            "surprised": "surprise",
            "calm": "neutral",
        }
        mapped_tags = self.emotion_map.get(emotion)
        if mapped_tags is None:
            mapped_tags = self.emotion_map.get(alias_map.get(emotion, emotion), self.emotion_map.get("neutral", []))
        query = " ".join(mapped_tags)

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.song_matrix).flatten()
        
        if randomize:
            # Get top 50 candidates and randomly sample with probability weights
            candidate_count = min(50, len(sims))
            top_candidates_indices = sims.argsort()[::-1][:candidate_count]
            top_candidates_scores = sims[top_candidates_indices]
            
            # Normalize scores to probabilities (higher score = higher probability)
            min_score = top_candidates_scores.min()
            adjusted_scores = top_candidates_scores - min_score + 0.1
            probabilities = adjusted_scores / adjusted_scores.sum()
            
            # Randomly sample top_k songs without replacement
            selected_positions = np.random.choice(
                len(top_candidates_indices), 
                size=min(top_k, len(top_candidates_indices)), 
                replace=False, 
                p=probabilities
            )
            selected_indices = top_candidates_indices[selected_positions]
            selected_scores = sims[selected_indices]
        else:
            # Return deterministic top_k matches
            selected_indices = sims.argsort()[::-1][:top_k]
            selected_scores = sims[selected_indices]

        rows = self.df.iloc[selected_indices].copy()
        rows["score"] = selected_scores

        return [
            {
                "track_id": int(row["track_id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "tags": row["tags"],
                "score": round(float(row["score"]), 4),
                "preview_url": get_song_preview_url(str(row["title"]), str(row["artist"])),
            }
            for _, row in rows.iterrows()
        ]
