from __future__ import annotations

import requests
from typing import Any

from ..config import LASTFM_API_KEY


def get_lastfm_preview_url(track_title: str, artist_name: str) -> dict[str, Any]:
    """
    Get preview URL and track info from Last.fm API.
    
    Args:
        track_title: Title of the track
        artist_name: Name of the artist
        
    Returns:
        Dictionary with preview URL and track info
    """
    if not LASTFM_API_KEY:
        return {"preview_url": None, "source": "none", "error": "Last.fm API key not configured"}
    
    try:
        # Search for track on Last.fm
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "track.search",
            "track": track_title,
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": 1,
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results", {}).get("trackmatches", {}).get("track"):
            return {"preview_url": None, "source": "none", "error": "Track not found on Last.fm"}
        
        track = data["results"]["trackmatches"]["track"][0]
        
        # Try to get preview URL
        preview_url = None
        if track.get("image"):
            # Use the track URL as fallback
            preview_url = track.get("url")
        
        # Try to get track info with preview
        if track.get("mbid"):
            detail_params = {
                "method": "track.getInfo",
                "api_key": LASTFM_API_KEY,
                "mbid": track["mbid"],
                "format": "json",
                "autocorrect": 1,
            }
            detail_response = requests.get(url, params=detail_params, timeout=5)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get("track", {}).get("image"):
                    preview_url = detail_data["track"].get("url")
        
        return {
            "preview_url": preview_url or f"https://www.youtube.com/results?search_query={artist_name}+{track_title}",
            "source": "lastfm",
            "track_url": track.get("url"),
            "listeners": track.get("listeners", "N/A"),
        }
        
    except requests.RequestException as e:
        return {"preview_url": None, "source": "error", "error": str(e)}
    except (KeyError, ValueError) as e:
        return {"preview_url": None, "source": "error", "error": f"Parse error: {str(e)}"}


def get_youtube_music_url(track_title: str, artist_name: str) -> str:
    """
    Generate a YouTube Music search URL for a track.
    """
    return f"https://music.youtube.com/search?q={artist_name}+{track_title}".replace(" ", "+")


def get_song_preview_url(track_title: str, artist_name: str) -> str:
    """
    Get a playable preview URL for a song.
    Falls back to YouTube Music search if Last.fm fails.
    """
    lastfm_result = get_lastfm_preview_url(track_title, artist_name)
    
    if lastfm_result.get("preview_url"):
        return lastfm_result["preview_url"]
    
    # Fallback to YouTube Music search
    return get_youtube_music_url(track_title, artist_name)
