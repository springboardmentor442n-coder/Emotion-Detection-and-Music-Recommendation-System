from fastapi import FastAPI
from backend.text_models import predict_emotion
from backend.music_recommender import recommend_songs

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend running"}

@app.post("/recommend")
def recommend(text: str):
    emotion = predict_emotion(text)
    songs = recommend_songs(emotion)

    return {
        "emotion": emotion,
        "songs": songs
    }