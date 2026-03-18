"""
CNN-based facial emotion predictor for MoodMate.

Uses a custom CNN model trained on FER-2013 dataset.
Model file: saved_models/best_model.keras
"""
import os
import numpy as np
from tensorflow import keras
from PIL import Image

# Emotion label order as per project spec (index maps to class)
EMOTION_LABELS = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Load model once at module level to avoid reloading on every request
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'saved_models', 'best_model.keras')
_cnn_model = keras.models.load_model(MODEL_PATH)


def preprocess_image(image) -> np.ndarray:
    """
    Preprocess image for CNN inference.

    Steps:
        1. Convert to grayscale
        2. Resize to 48×48
        3. Normalize pixel values to [0, 1]
        4. Reshape to (1, 48, 48, 1)

    Args:
        image: A PIL Image object.

    Returns:
        Preprocessed numpy array ready for model prediction.
    """
    image = image.convert('L')          # Grayscale
    image = image.resize((48, 48))      # Resize to 48×48
    img_array = np.array(image) / 255.0  # Normalize to [0, 1]
    img_array = img_array.reshape(1, 48, 48, 1)  # Reshape for model
    return img_array


def predict_emotion(image) -> str:
    """
    Predict the emotion from a facial image.

    Args:
        image: A PIL Image object of a face.

    Returns:
        One of the 6 MoodMate emotion labels:
        'angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'
    """
    processed = preprocess_image(image)
    predictions = _cnn_model.predict(processed)
    emotion_index = np.argmax(predictions)
    return EMOTION_LABELS[emotion_index]


if __name__ == "__main__":
    print("CNN Predictor loaded successfully.")
    print(f"Model path: {MODEL_PATH}")
    print(f"Emotion labels: {EMOTION_LABELS}")
