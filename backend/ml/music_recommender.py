import pandas as pd
import random
import os

class MusicRecommender:
    def __init__(self, dataset_path: str):
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        self.df = pd.read_csv(dataset_path)
        self._normalize_columns()

    def _normalize_columns(self):
        """
        Intelligently auto-map user CSV columns to the unified standard 
        expected by the UI (Song, Artist, Genre, Link, Mood), regardless of 
        what their specific CSV headers are named.
        """
        col_map = {}
        for col in self.df.columns:
            c = str(col).lower().replace('_', '').replace('-', '').replace(' ', '')
            if 'song' in c or 'trackname' in c or 'title' in c:
                col_map[col] = 'Song'
            elif 'artist' in c or 'band' in c:
                col_map[col] = 'Artist'
            elif 'genre' in c or 'tag' in c:
                col_map[col] = 'Genre'
            elif 'preview' in c or 'url' in c or 'link' in c:
                if 'Link' not in col_map.values(): # assign first match
                    col_map[col] = 'Link'
            elif 'mood' in c or 'emotion' in c:
                col_map[col] = 'Mood'
        
        self.df.rename(columns=col_map, inplace=True)
        
        # Ensure core columns exist, use positional fallbacks if missing
        if 'Song' not in self.df.columns:
            # Assumes 2nd column is track name usually
            self.df['Song'] = self.df.iloc[:, 1] if len(self.df.columns) > 1 else "Unknown Song"
        if 'Artist' not in self.df.columns:
            # Assumes 3rd column is artist usually
            self.df['Artist'] = self.df.iloc[:, 2] if len(self.df.columns) > 2 else "Unknown Artist"
        if 'Link' not in self.df.columns:
            # Try to grab the first string column that contains 'http'
            http_cols = [c for c in self.df.columns if self.df[c].dtype == 'object' and self.df[c].astype(str).str.contains('http').any()]
            self.df['Link'] = self.df[http_cols[0]] if http_cols else ""
        if 'Genre' not in self.df.columns:
            self.df['Genre'] = "Mixed"

    def recommend(self, emotion: str, num_recommendations: int = 4) -> list:
        emotion = emotion.lower()
        matching_songs = pd.DataFrame()
        
        # 1. Standard approach: If a 'Mood' column was explicitly provided
        if 'Mood' in self.df.columns:
            matching_songs = self.df[self.df['Mood'].astype(str).str.lower() == emotion]
            
        # 2. Spotify Audio Features logic: If user dataset contains valence/energy
        elif 'valence' in self.df.columns and 'energy' in self.df.columns:
            if emotion == 'happy':
                matching_songs = self.df.query('valence > 0.6 & energy > 0.6')
            elif emotion == 'sad':
                matching_songs = self.df.query('valence < 0.4 & energy < 0.4')
            elif emotion == 'angry':
                matching_songs = self.df.query('valence < 0.4 & energy > 0.7')
            elif emotion == 'surprise' or emotion == 'surprised':
                matching_songs = self.df.query('energy > 0.8')
            elif emotion == 'fear' or emotion == 'fearful':
                matching_songs = self.df.query('valence < 0.3 & energy > 0.5')
            elif emotion == 'disgust':
                matching_songs = self.df.query('valence < 0.4')
            else: # neutral
                matching_songs = self.df.query('valence >= 0.4 & valence <= 0.6')
                
        # 3. Fallback: Completely random recommendations if no logical filters exist
        if matching_songs.empty:
            matching_songs = self.df
            
        sample_size = min(num_recommendations, len(matching_songs))
        recommendations = matching_songs.sample(n=sample_size).to_dict('records')
        
        # Clean NaNs
        for rec in recommendations:
            for k, v in rec.items():
                if pd.isna(v):
                    rec[k] = ""
                    
        return recommendations
