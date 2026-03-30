import tensorflow as tf
import numpy as np
import cv2
import os

# Path to your model
MODEL_PATH = r"C:\Emotion-Music-Recommender\models\model.keras"

# Load model once
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    model = None

emotions = ['Angry', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

def predict_emotion(image_bytes):
    if model is None: return "Neutral"
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (48, 48))
    img = img / 255.0
    img = np.reshape(img, (1, 48, 48, 1))
    prediction = model.predict(img)
    return emotions[np.argmax(prediction)]