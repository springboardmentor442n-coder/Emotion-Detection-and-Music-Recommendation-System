import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ml.text_classifier import TextEmotionClassifier
from ml.image_classifier import ImageEmotionClassifier
from ml.music_recommender import MusicRecommender

app = FastAPI(title="MoodMate API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

text_classifier = None
image_classifier = None
music_recommender = None

print("Initializing Machine Learning Models (this might take a few seconds on first run)...")

try:
    text_classifier = TextEmotionClassifier()
    print("Text Model Loaded.")
except Exception as e:
    print(f"Error loading Text Model: {e}")

try:
    image_classifier = ImageEmotionClassifier()
    print("Image Model Loaded.")
except Exception as e:
    print(f"Error loading Image Model: {e}")

try:
    music_recommender = MusicRecommender(os.path.join(os.path.dirname(__file__), "data", "music_dataset.csv"))
    print("Music Recommender Loaded.")
except Exception as e:
    print(f"Error loading Music Recommender: {e}")

class TextRequest(BaseModel):
    text: str

class ImageBase64Request(BaseModel):
    image_base64: str

@app.post("/api/predict/text")
async def predict_text(request: TextRequest):
    if text_classifier is None:
        raise HTTPException(status_code=500, detail="Text classification model failed to safely load in backend. Please check terminal logs for the exact error (e.g. download failed).")
        
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    result = text_classifier.predict(request.text)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    emotion = result["emotion"]
    recommendations = music_recommender.recommend(emotion, num_recommendations=4)
    
    return {
        "emotion": emotion,
        "confidence": result["confidence"],
        "recommendations": recommendations
    }

@app.post("/api/predict/image")
async def predict_image(request: ImageBase64Request):
    if image_classifier is None:
        raise HTTPException(status_code=500, detail="Image classification model failed to safely load in backend. Please check terminal logs for the exact error.")
        
    if not request.image_base64:
        raise HTTPException(status_code=400, detail="Image cannot be empty")
        
    result = image_classifier.predict_from_base64(request.image_base64)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    emotion = result["emotion"]
    recommendations = music_recommender.recommend(emotion, num_recommendations=4)
    
    return {
        "emotion": emotion,
        "confidence": result["confidence"],
        "recommendations": recommendations
    }

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
