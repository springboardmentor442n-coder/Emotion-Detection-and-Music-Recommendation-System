import os
import base64
import numpy as np
import cv2
import tensorflow as tf

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import io

from recommender import get_recommendations
from emotion_predictor import predict_emotion

# ── Load .env ────────────────────────────────────────────────

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
app = Flask(__name__,
    static_folder=os.path.join(FRONTEND_DIR, 'static'),
    template_folder=os.path.join(FRONTEND_DIR, 'templates')
)
CORS(app)

EMOTION_LABELS = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

EMOTION_EMOJI = {
    'angry':    '😠',
    'fear':     '😨',
    'happy':    '😊',
    'neutral':  '😐',
    'sad':      '😢',
    'surprise': '😲'
}

# ── Load model ───────────────────────────────────────────────
MODEL_PATH = os.path.join(BACKEND_DIR, 'emotion_model_final.h5')
try:
    _emotion_model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded ✅ | Input shape: {_emotion_model.input_shape}")
except Exception as e:
    print(f"Warning: Could not load model. Error: {e}")
    _emotion_model = None


def preprocess_image(base64_string):
    # Strip header
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    img_bytes = base64.b64decode(base64_string)

    # Convert to grayscale numpy array
    img = Image.open(io.BytesIO(img_bytes)).convert('L')  # L = grayscale
    img_array = np.array(img)

    # Detect face and crop
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(
        img_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        img_array = img_array[y:y+h, x:x+w]
        print(f"Face detected at x={x} y={y} w={w} h={h}")
    else:
        print("No face detected, using full image")

    # Resize to exactly 48x48
    img_array = cv2.resize(img_array, (48, 48))
    img_array = img_array.astype(np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=-1)  # (48,48) → (48,48,1)
    img_array = np.expand_dims(img_array, axis=0)   # (48,48,1) → (1,48,48,1)
    return img_array


# ── Route 1: Image → Emotion + Songs ────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    if _emotion_model is None:
        return jsonify({'error': 'Emotion model not loaded.'}), 500

    data = request.get_json()
    image_base64 = data.get('image', '')

    if not image_base64:
        return jsonify({'error': 'No image provided.'}), 400

    try:
        img_array = preprocess_image(image_base64)
        predictions = _emotion_model.predict(img_array)[0]

        print("Raw predictions:", {EMOTION_LABELS[i]: round(float(predictions[i])*100,1) for i in range(len(EMOTION_LABELS))})

        all_scores = {
            label: round(float(predictions[i]) * 100, 1)
            for i, label in enumerate(EMOTION_LABELS)
        }

        top_index   = int(np.argmax(predictions))
        top_emotion = EMOTION_LABELS[top_index]
        confidence  = round(float(predictions[top_index]) * 100, 1)
        emoji       = EMOTION_EMOJI.get(top_emotion, '🎵')

        raw_songs = get_recommendations(top_emotion, top_n=5)
        songs = [
            {
                'song': r.get('name', ''),
                'artist': r.get('artist', ''),
                'preview_url': r.get('preview_url', ''),  # ← was missing
            }
            for r in raw_songs
        ]

        return jsonify({
            'emotion':    top_emotion,
            'emoji':      emoji,
            'confidence': confidence,
            'all_scores': all_scores,
            'songs':      songs
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


# ── Route 2: Text → Emotion + Songs ─────────────────────────
@app.route('/predict-text', methods=['POST'])
def predict_text():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    try:
        emotion  = predict_emotion(text)
        emoji    = EMOTION_EMOJI.get(emotion, '🎵')
        raw_songs = get_recommendations(emotion, top_n=5)
        songs = [
            {
                'song': r.get('name', ''),
                'artist': r.get('artist', ''),
                'preview_url': r.get('preview_url', ''),
            }
            for r in raw_songs
        ]
        return jsonify({'emotion': emotion, 'emoji': emoji, 'songs': songs})

    except Exception as e:
        print(f"Text prediction error: {e}")
        return jsonify({'error': str(e)}), 500



# ── Route 4: Serve frontend ──────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)