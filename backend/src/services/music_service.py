from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from ..config import LASTFM_API_KEY
from ..recommendation.engine import MusicRecommender

EMOTION_TO_TAG = {
    "happy": "pop",
    "sad": "blues",
    "calm": "ambient",
    "angry": "rock",
    "surprised": "electronic",
    "fearful": "instrumental",
    "neutral": "lofi",
}


class MusicService:
    def __init__(self, songs_csv_path: Path, emotion_map_path: Path) -> None:
        self.recommender = MusicRecommender(songs_csv_path=songs_csv_path, emotion_map_path=emotion_map_path)

    def _lastfm_tracks(self, emotion: str, limit: int) -> list[dict[str, Any]]:
        if not LASTFM_API_KEY:
            return []

        tag = EMOTION_TO_TAG.get(emotion, "chill")
        url = (
            "https://ws.audioscrobbler.com/2.0/"
            f"?method=tag.gettoptracks&tag={tag}&api_key={LASTFM_API_KEY}&format=json&limit={limit}"
        )
        try:
            res = requests.get(url, timeout=8)
            if res.status_code != 200:
                return []
            payload = res.json()
            tracks = payload.get("tracks", {}).get("track", []) or []
            normalized = []
            for idx, item in enumerate(tracks, start=1):
                normalized.append(
                    {
                        "track_id": 100000 + idx,
                        "title": item.get("name", "Unknown"),
                        "artist": (item.get("artist") or {}).get("name", "Unknown"),
                        "genre": tag,
                        "tags": f"{emotion} {tag}",
                        "score": 0.9 - (idx * 0.02),
                        "source": "lastfm",
                    }
                )
            return normalized
        except requests.RequestException:
            return []

    def recommend(self, emotion: str, top_k: int = 10) -> list[dict[str, Any]]:
        local = self.recommender.recommend(emotion=emotion, top_k=top_k)
        for song in local:
            song["source"] = "mock-db"

        external = self._lastfm_tracks(emotion=emotion, limit=max(4, min(top_k, 10)))
        blended = (external + local)[:top_k]
        return blended
