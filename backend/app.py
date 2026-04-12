import os
import base64
import numpy as np
import cv2

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import io

from recommender import get_recommendations
from emotion_predictor import predict_emotion
from emotion_image_predictor import predict_emotion_from_image

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
print("✅ Emotion detection models loaded:")
print("   - Text-based: HuggingFace RoBERTa (GoEmotions)")
print("   - Image-based: PyTorch CNN")


# ── Route 1: Image → Emotion + Songs ────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_base64 = data.get('image', '')

    if not image_base64:
        return jsonify({'error': 'No image provided.'}), 400

    try:
        result = predict_emotion_from_image(image_base64)
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Unknown error')}), 400
        
        top_emotion = result['emotion']
        confidence = result['confidence']
        all_scores = result['all_scores']
        emoji = EMOTION_EMOJI.get(top_emotion, '🎵')

        raw_songs = get_recommendations(top_emotion, top_n=5)
        songs = [
            {
                'song': r.get('name', ''),
                'artist': r.get('artist', ''),
                'preview_url': r.get('preview_url', ''),
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


# ── Route 3: Serve frontend ──────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)