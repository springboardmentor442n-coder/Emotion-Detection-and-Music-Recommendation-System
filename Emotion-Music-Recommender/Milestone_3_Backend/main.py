from fastapi import FastAPI, UploadFile, File, Body
import pandas as pd
import os
from image_models import predict_emotion
from textblob import TextBlob

app = FastAPI()

# Load Data
CSV_PATH = r"C:\Emotion-Music-Recommender\data\spotify_millsongdata.csv"
df = pd.read_csv(CSV_PATH)

def get_songs_for_emotion(emotion):
    mood_map = {
        "Happy": "joy", "Sad": "lonely", "Angry": "fire",
        "Neutral": "dream", "Surprise": "magic", "Fear": "night"
    }
    keyword = mood_map.get(emotion, "music")
    # Get 3 random songs
    results = df[df['text'].str.contains(keyword, case=False, na=False)].sample(3)
    songs = []
    for _, row in results.iterrows():
        songs.append({
            "title": row['song'],
            "artist": row['artist'],
            "url": f"https://open.spotify.com/search/{row['song']} {row['artist']}".replace(" ", "%20")
        })
    return songs

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    emotion = predict_emotion(contents)
    return {"emotion": emotion, "songs": get_songs_for_emotion(emotion)}

@app.post("/predict_text")
async def predict_text(data: dict = Body(...)):
    text = data.get("text", "")
    blob = TextBlob(text).sentiment.polarity
    emotion = "Happy" if blob > 0 else "Sad" if blob < 0 else "Neutral"
    return {"emotion": emotion, "songs": get_songs_for_emotion(emotion)}