from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .services.music_service import MusicService
from .services.openai_emotion import detect_emotion_from_image_bytes, detect_emotion_from_text
from .storage.mongo_store import MongoStore

app = FastAPI(title="MoodMate API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
FRONTEND_INDEX = BASE_DIR.parent / "frontend" / "index.html"

music_service = MusicService(
    songs_csv_path=DATA_DIR / "sample_songs.csv",
    emotion_map_path=DATA_DIR / "emotion_music_map.json",
)
mongo_store = MongoStore()


class TextEmotionRequest(BaseModel):
    text: str
    top_k: int = 10


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def frontend_ui() -> FileResponse:
    return FileResponse(FRONTEND_INDEX)


@app.post("/api/detect-emotion-text")
def detect_from_text(payload: TextEmotionRequest) -> dict:
    detection = detect_emotion_from_text(payload.text)
    recommendations = music_service.recommend(emotion=detection["emotion"], top_k=payload.top_k)
    response = {"input_mode": "text", **detection, "recommendations": recommendations}
    mongo_store.save_session(response)
    return response


@app.post("/api/detect-emotion-image")
async def detect_from_image(file: UploadFile = File(...), top_k: int = Form(5)) -> dict:
    image_bytes = await file.read()
    detection = detect_emotion_from_image_bytes(image_bytes=image_bytes, filename=file.filename or "upload.jpg")
    recommendations = music_service.recommend(emotion=detection["emotion"], top_k=top_k)
    response = {"input_mode": "image", **detection, "recommendations": recommendations}
    mongo_store.save_session(response)
    return response


class RecommendRequest(BaseModel):
    emotion: str
    top_k: int = 10


@app.post("/api/recommend-music")
def recommend_music(payload: RecommendRequest) -> dict:
    songs = music_service.recommend(emotion=payload.emotion, top_k=payload.top_k)
    response = {"emotion": payload.emotion, "recommendations": songs}
    mongo_store.save_session({"input_mode": "recommend-only", **response})
    return response


@app.get("/api/history")
def history(limit: int = 20) -> dict:
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    return {
        "mongo_enabled": mongo_store.is_enabled(),
        "sessions": mongo_store.get_sessions(limit=limit),
    }


@app.get("/api/search")
def search_songs(q: str, limit: int = 10) -> dict:
    """Search for songs by title or artist."""
    if not q or not q.strip():
        return {"results": []}
    
    if limit < 1:
        limit = 1
    if limit > 50:
        limit = 50
    
    query = q.lower().strip()
    
    # Search in title and artist columns
    mask = (
        music_service.df["title"].str.lower().str.contains(query, na=False) |
        music_service.df["artist"].str.lower().str.contains(query, na=False)
    )
    
    results_df = music_service.df[mask].head(limit).copy()
    
    from .services.music_preview_service import get_song_preview_url
    
    return {
        "results": [
            {
                "track_id": int(row["track_id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "tags": row["tags"],
                "preview_url": get_song_preview_url(str(row["title"]), str(row["artist"])),
            }
            for _, row in results_df.iterrows()
        ]
    }
