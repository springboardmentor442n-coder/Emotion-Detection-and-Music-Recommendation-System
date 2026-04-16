"""
emotion_predictor.py
────────────────────
Loads the trained CNN and predicts the emotion from:
  • A single image file path
  • A numpy array (e.g. from webcam frame)

Returns the predicted emotion label + confidence scores.
"""

import os
import sys
import numpy as np

# So we can import sibling modules from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.preprocess import load_image_for_prediction, IMG_SIZE, EMOTION_LABELS

# ──────────────────────────────────────────────────────────────────────────────
# Lazy-loaded model (loaded once on first call, then cached)
# ──────────────────────────────────────────────────────────────────────────────
_model = None

BASE_DIR    = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "models", "emotion_model.h5")


def _load_model():
    """Load the Keras model from disk (only once)."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}.\n"
                "Please run: python src/train_model.py"
            )
        import tensorflow as tf
        _model = tf.keras.models.load_model(MODEL_PATH)
        print(f"✅ Emotion model loaded from {MODEL_PATH}")
    return _model


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def predict_from_path(image_path: str) -> dict:
    """
    Predict emotion from an image file.

    Args:
        image_path: Path to a JPG/PNG image of a face.

    Returns:
        {
          "emotion":     "happy",
          "confidence":  0.92,
          "all_scores":  {"angry": 0.01, "happy": 0.92, ...}
        }
    """
    model = _load_model()
    img_array = load_image_for_prediction(image_path)   # shape (1,48,48,1)
    return _run_prediction(model, img_array)


def predict_from_array(face_array: np.ndarray) -> dict:
    """
    Predict emotion from a numpy array of a cropped face.

    Args:
        face_array: Grayscale numpy array of shape (H, W) or (H, W, 1).
                    Will be resized to 48×48 automatically.

    Returns:
        Same dict as predict_from_path()
    """
    from PIL import Image

    model = _load_model()

    # Handle different input shapes
    if face_array.ndim == 3 and face_array.shape[2] != 1:
        # Convert BGR colour image (OpenCV) to grayscale
        import cv2
        face_array = cv2.cvtColor(face_array, cv2.COLOR_BGR2GRAY)

    if face_array.ndim == 3:
        face_array = face_array[:, :, 0]  # drop channel dim

    # Resize & normalise
    img = Image.fromarray(face_array.astype(np.uint8)).resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img, dtype="float32") / 255.0
    arr = arr.reshape(1, IMG_SIZE, IMG_SIZE, 1)

    return _run_prediction(model, arr)


def _run_prediction(model, img_array: np.ndarray) -> dict:
    """Run inference and build the result dictionary."""
    preds = model.predict(img_array, verbose=0)[0]   # shape (7,)
    top_idx = int(np.argmax(preds))
    return {
        "emotion":    EMOTION_LABELS[top_idx],
        "confidence": float(preds[top_idx]),
        "all_scores": {label: float(preds[i])
                       for i, label in enumerate(EMOTION_LABELS)},
    }


# ──────────────────────────────────────────────────────────────────────────────
# DEMO (run as script)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/emotion_predictor.py <path_to_image>")
        sys.exit(1)

    result = predict_from_path(sys.argv[1])
    print(f"\n🎭 Detected emotion : {result['emotion'].upper()}")
    print(f"   Confidence       : {result['confidence']*100:.1f}%")
    print("\n   All scores:")
    for emo, score in sorted(result["all_scores"].items(),
                              key=lambda x: -x[1]):
        bar = "█" * int(score * 30)
        print(f"   {emo:10s} {score*100:5.1f}% {bar}")
