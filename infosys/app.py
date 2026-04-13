from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import tensorflow as tf
import pandas as pd
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# ---------------- LOAD MODELS ----------------
image_model = tf.keras.models.load_model(
    r"C:\Users\ambat\OneDrive\Desktop\infosys (3) final\infosys\models\fer2013_emotion_model.h5"
)

emotion_labels = ['Angry', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# ---------------- LOAD DATASET ----------------
df = pd.read_csv(r"C:\Users\ambat\OneDrive\Desktop\music data\Music Info.csv")
df['tags'] = df['tags'].fillna('').str.lower()

# ---------------- IMAGE PREPROCESS ----------------
def preprocess_image(img):
    img = img.convert('L')
    img = img.resize((48, 48))
    img = np.array(img) / 255.0
    img = np.reshape(img, (1, 48, 48, 1))
    return img

# ---------------- TEXT EMOTION ----------------
EMOTION_MAPPING = {
    'joy': 'Happy',
    'love': 'Happy',
    'excitement': 'Happy',
    'amusement': 'Happy',
    'interest': 'Neutral',
    'satisfaction': 'Neutral',
    'calmness': 'Neutral',
    'sadness': 'Sad',
    'anger': 'Angry',
    'fear': 'Fear',
    'disgust': 'Angry',
    'surprise': 'Surprise'
}

TEXT_CLASSIFIER = pipeline(
    "text-classification",
    model="ayoubkirouane/BERT-Emotions-Classifier"
)

def detect_text_emotion(text):
    try:
        result = TEXT_CLASSIFIER(text)[0]
        raw_label = result['label'].lower()
        return EMOTION_MAPPING.get(raw_label, "Neutral")
    except Exception as e:
        print("Text Error:", e)
        return "Neutral"

# ---------------- RECOMMENDATION ----------------
def recommend_songs(emotion):

    if emotion == "Happy":
        filtered = df[
            ((df['valence'] > 0.6) & (df['energy'] > 0.5)) |
            (df['tags'].str.contains("happy|party"))
        ]

    elif emotion == "Sad":
        filtered = df[
            ((df['valence'] < 0.4) & (df['energy'] < 0.5)) |
            (df['tags'].str.contains("sad"))
        ]

    elif emotion == "Angry":
        filtered = df[
            ((df['valence'] < 0.5) & (df['energy'] > 0.7)) |
            (df['tags'].str.contains("angry|metal"))
        ]

    else:
        filtered = df.copy()

    filtered = filtered.drop_duplicates(subset="name")
    filtered = filtered[filtered['spotify_preview_url'].notna()]

    if len(filtered) == 0:
        fallback = df[df['spotify_preview_url'].notna()]
        if len(fallback) == 0:
            return []
        return fallback.sample(min(5, len(fallback)))[
            ['name', 'artist', 'spotify_preview_url']
        ].to_dict(orient="records")

    return filtered.sample(min(5, len(filtered)))[
        ['name', 'artist', 'spotify_preview_url']
    ].to_dict(orient="records")

# ---------------- ROUTE ----------------
@app.route('/predict', methods=['POST'])
def predict():
    print("Request received")

    # IMAGE
    if 'image' in request.files:
        file = request.files['image']
        img = Image.open(file)
        img = preprocess_image(img)

        preds = image_model.predict(img)
        idx = np.argmax(preds)

        emotion = emotion_labels[idx]
        confidence = float(np.max(preds)) * 100

        songs = recommend_songs(emotion)

        return jsonify({
            "emotion": emotion,
            "confidence": round(confidence, 2),
            "songs": songs
        })

    # TEXT
    if 'text' in request.form:
        text = request.form['text']

        if not text.strip():
            return jsonify({"error": "No text provided"}), 400

        emotion = detect_text_emotion(text)
        songs = recommend_songs(emotion)

        return jsonify({
            "emotion": emotion,
            "confidence": 0,
            "songs": songs
        })

    return jsonify({"error": "No input provided"}), 400

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "Backend is running successfully!"

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)