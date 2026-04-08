import pandas as pd
import numpy as np
import os
import json
import re
import urllib.parse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ======================================================
# 🔑 API Keys
# ======================================================
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
YOUTUBE_API_KEY       = os.getenv("YOUTUBE_API_KEY", "")
# ======================================================
# 🗂️ YouTube Video ID Cache (persisted to disk)
# ======================================================
_cache_path    = os.path.join(os.path.dirname(__file__), 'youtube_cache.json')
_youtube_cache = {}

if os.path.exists(_cache_path):
    with open(_cache_path, "r") as f:
        _youtube_cache = json.load(f)
    print(f"✅ Loaded YouTube cache with {len(_youtube_cache)} entries")
else:
    print("⚠️ No YouTube cache found — will build on demand")

def _save_cache():
    with open(_cache_path, "w") as f:
        json.dump(_youtube_cache, f, indent=2)

# ======================================================
# 1️⃣ Load Dataset
# ======================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), 'dataset.csv')

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

music_df = pd.read_csv(DATA_PATH)
music_df.columns = music_df.columns.str.strip().str.lower()
music_df = music_df.drop(columns=['unnamed: 0'], errors='ignore')
music_df = music_df.dropna(subset=['valence', 'energy'])

# ✅ Auto-detect correct column names
TRACK_COL  = 'name'   if 'name'   in music_df.columns else 'track_name'
ARTIST_COL = 'artist' if 'artist' in music_df.columns else 'artists'

print(f"✅ Loaded dataset with {len(music_df)} tracks")
print(f"   Using columns: track='{TRACK_COL}', artist='{ARTIST_COL}'")

# ======================================================
# 2️⃣ Spotify
# ======================================================
def get_spotify_token():
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
            timeout=10
        )
        if response.status_code != 200 or not response.text.strip():
            return None
        return response.json().get("access_token")
    except Exception as e:
        print("Spotify token error:", e)
        return None


def get_spotify_data(track_name, artist):
    """
    Returns dict with:
      - preview_url  : 30s mp3 clip (or None)
      - spotify_url  : full track page (or search fallback)
    """
    search_fallback = f"https://open.spotify.com/search/{urllib.parse.quote(f'{track_name} {artist}')}"
    result = {"preview_url": None, "spotify_url": search_fallback}

    try:
        token = get_spotify_token()
        if not token:
            return result

        headers  = {"Authorization": f"Bearer {token}"}
        params   = {"q": f"{track_name} {artist}", "type": "track", "limit": 1}
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers, params=params, timeout=10
        )
        if response.status_code != 200 or not response.text.strip():
            return result

        items = response.json().get("tracks", {}).get("items", [])
        if items:
            result["preview_url"] = items[0].get("preview_url")
            result["spotify_url"] = items[0].get("external_urls", {}).get("spotify", search_fallback)
    except Exception as e:
        print("Spotify search error:", e)

    return result


# ======================================================
# 3️⃣ YouTube — API first, scrape as fallback
# ======================================================
_YT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _youtube_api_search(query: str):
    """Official YouTube Data API v3 search. Uses ~100 quota units."""
    if not YOUTUBE_API_KEY:
        return None
    try:
        url    = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part":       "snippet",
            "q":          query,
            "type":       "video",
            "maxResults": 1,
            "key":        YOUTUBE_API_KEY
        }
        resp  = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0]["id"]["videoId"]
        elif resp.status_code == 403:
            print("⚠️ YouTube API quota exceeded — switching to scrape fallback")
    except Exception as e:
        print(f"YouTube API error: {e}")
    return None


def _youtube_scrape_search(query: str):
    """
    Fallback: scrapes YouTube search page for a video ID.
    No API key needed. Fragile — use only when API fails/quota exceeded.
    """
    try:
        url  = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        resp = requests.get(url, headers=_YT_HEADERS, timeout=10)
        ids  = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        if ids:
            return ids[0]
    except Exception as e:
        print(f"YouTube scrape error: {e}")
    return None


def get_youtube_video_id(track_name: str, artist: str):
    """
    Fallback chain:
      1. Cache          — free, instant
      2. YouTube API    — official, reliable (100 units/search)
      3. Scrape         — last resort, no API key needed
      4. None           — cached so we don't retry
    """
    cache_key = f"{track_name}_{artist}"

    # 1.Cache
    if cache_key in _youtube_cache:
        return _youtube_cache[cache_key]

    query    = f"{track_name} {artist} official audio"
    video_id = None

    # 2.YouTube API
    video_id = _youtube_api_search(query)
    if video_id:
        print(f"✅ YouTube API: {track_name} → {video_id}")

    # 3.Scrape fallback
    if not video_id:
        print(f"Falling back to scrape for: {track_name}")
        video_id = _youtube_scrape_search(query)
        if video_id:
            print(f"YouTube scrape: {track_name} → {video_id}")

    # 4.Cache result (even None — avoids retrying dead-end tracks)
    _youtube_cache[cache_key] = video_id
    _save_cache()

    if not video_id:
        print(f" No YouTube ID found for: {track_name}")

    return video_id


def get_youtube_urls(track_name: str, artist: str):
    """
    Returns:
      - embed_url  : embeddable player URL (or None if no ID found)
      - search_url : always-valid YouTube search link (final safety net)
    """
    video_id   = get_youtube_video_id(track_name, artist)
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(f'{track_name} {artist}')}"
    embed_url  = f"https://www.youtube.com/embed/{video_id}?autoplay=0&rel=0" if video_id else None

    return {"embed_url": embed_url, "search_url": search_url}


# ======================================================
# 4️⃣ Core Recommendation Function
# ======================================================
def recommend_songs_by_emotion(emotion: str, n: int = 5, uplift: bool = False):
    emotion = emotion.lower().strip()

    if not uplift:
        if emotion == "sad":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"] < 0.5)]
        elif emotion == "happy":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"] > 0.5)]
        elif emotion == "angry":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"] > 0.7)]
        elif emotion == "surprise":
            recs = music_df[(music_df["valence"].between(0.4, 0.7)) & (music_df["energy"] > 0.6)]
        elif emotion == "fear":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"].between(0.6, 1.0))]
        else:  # neutral
            recs = music_df[(music_df["valence"].between(0.4, 0.6)) & (music_df["energy"].between(0.4, 0.6))]
    else:
        if emotion == "sad":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"].between(0.4, 0.7))]
        elif emotion == "angry":
            recs = music_df[(music_df["valence"] > 0.5) & (music_df["energy"] < 0.5)]
        elif emotion == "fear":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"].between(0.3, 0.6))]
        elif emotion == "happy":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"] > 0.5)]
        elif emotion == "surprise":
            recs = music_df[(music_df["valence"].between(0.5, 0.8)) & (music_df["energy"] > 0.6)]
        else:  # neutral
            recs = music_df[(music_df["valence"].between(0.4, 0.6)) & (music_df["energy"].between(0.4, 0.6))]

    if recs.empty:
        print(f"⚠️ No songs found for emotion='{emotion}', uplift={uplift} — using random sample")
        recs = music_df.sample(n)

    recs_sampled = recs.sample(min(n, len(recs)))

    results = []
    for _, row in recs_sampled.iterrows():
        track_name  = str(row.get(TRACK_COL,  "Unknown"))
        artist      = str(row.get(ARTIST_COL, "Unknown"))

        yt_urls     = get_youtube_urls(track_name, artist)
        spotify     = get_spotify_data(track_name, artist)

        results.append({
            "name":              track_name,
            "artist":            artist,
            # YouTube
            "youtube_embed_url": yt_urls["embed_url"],   # None if not found
            "youtube_link":      yt_urls["search_url"],  # always valid
            # Spotify
            "spotify_preview":   spotify["preview_url"], # 30s clip or None
            "spotify_link":      spotify["spotify_url"], # full page or search
        })

    return results


# ======================================================
# 5️⃣ Local Test
# ======================================================
if __name__ == "__main__":
    for emotion in ["happy", "sad"]:
        print(f"\n🎵 Recommendations for: {emotion}")
        songs = recommend_songs_by_emotion(emotion, n=2)
        for s in songs:
            print(f"  {s['name']} - {s['artist']}")
            print(f"    YT Embed:        {s['youtube_embed_url']}")
            print(f"    YT Search:       {s['youtube_link']}")
            print(f"    Spotify Preview: {s['spotify_preview']}")
            print(f"    Spotify Page:    {s['spotify_link']}")