from flask import Flask, request, jsonify
from flask_cors import CORS

from text_emotion import predict_emotion
from music_mapper import recommend_songs_by_emotion

import cv2
import numpy as np
import base64

from face_emotion import detect_emotion_from_image

app = Flask(__name__)
CORS(app)


# ---------------- TEXT ROUTE ----------------
@app.route("/text", methods=["POST"])
def text_route():
    data = request.json
    text = data.get("text", "")
    uplift = data.get("uplift", False)

    emotion = predict_emotion(text)
    songs = recommend_songs_by_emotion(emotion, n=5, uplift=uplift)

    return jsonify({
        "emotion": emotion,
        "songs": songs
    })


# ---------------- IMAGE UPLOAD ROUTE ----------------
@app.route("/upload", methods=["POST"])
def upload_route():
    try:
        file = request.files.get("file")
        uplift = request.form.get("uplift", "false").lower() == "true"

        if not file:
            return jsonify({"error": "No file"}), 400

        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # detect_emotion_from_image returns (emotion, confidence)
        emotion, confidence = detect_emotion_from_image(img)
        songs = recommend_songs_by_emotion(emotion, n=5, uplift=uplift)

        return jsonify({
            "emotion": emotion,
            "confidence": round(confidence, 3),
            "songs": songs
        })

    except Exception as e:
        print("Upload Error:", e)
        return jsonify({"error": "Server error"}), 500


# ---------------- REAL-TIME WEBCAM ROUTE ----------------
@app.route("/detect-face", methods=["POST"])
def detect_face():
    try:
        data = request.json

        if not data or "image" not in data:
            return jsonify({"error": "No image provided"}), 400

        image_data = data["image"]
        uplift = data.get("uplift", False)

        # Remove base64 header if present (e.g. "data:image/jpeg;base64,...")
        if "," in image_data:
            image_data = image_data.split(",")[1]

        try:
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return jsonify({"error": "Invalid base64"}), 400

        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        emotion, confidence = detect_emotion_from_image(img)
        songs = recommend_songs_by_emotion(emotion, n=5, uplift=uplift)

        return jsonify({
            "emotion": emotion,
            "confidence": round(confidence, 3),
            "songs": songs
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)