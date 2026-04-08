import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from keras.models import load_model

# ─────────────────────────────────────────────────────────────────
# PERFORMANCE FIX 1: limit TensorFlow to 2 CPU threads so it
# doesn't fight with Flask/MediaPipe for cores on a laptop CPU.
# ─────────────────────────────────────────────────────────────────
tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(2)

# Load model once at import time
model = load_model("../ml/models/emotion_model.keras")

# ─────────────────────────────────────────────────────────────────
# PERFORMANCE FIX 2: warm-up the model with a dummy prediction so
# the FIRST real request doesn't pay the Keras graph-build cost.
# Without this, the first call takes 10-20 s on CPU.
# ─────────────────────────────────────────────────────────────────
_dummy = np.zeros((1, 48, 48, 1), dtype="float32")
model.predict(_dummy, verbose=0)
print("[face_emotion] Model warmed up ✓")

emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# ─────────────────────────────────────────────────────────────────
# PERFORMANCE FIX 3: reuse a single MediaPipe FaceDetection instance
# (creating one per request is expensive).
# model_selection=0 → short-range (≤2 m), fastest option.
# ─────────────────────────────────────────────────────────────────
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)


def detect_emotion_from_image(frame: np.ndarray):
    """
    Returns (emotion: str, confidence: float).
    frame must be a BGR numpy array (from cv2).
    """
    if frame is None or frame.size == 0:
        return "Neutral", 0.0

    h, w = frame.shape[:2]

    # ─────────────────────────────────────────────────────────────
    # PERFORMANCE FIX 4: downscale large frames before MediaPipe.
    # A 1080p frame → 480p cuts detection time by ~4×.
    # We still use the original crop for the model input.
    # ─────────────────────────────────────────────────────────────
    scale = 1.0
    if max(h, w) > 480:
        scale = 480 / max(h, w)
        small = cv2.resize(frame, (int(w * scale), int(h * scale)))
    else:
        small = frame

    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    results   = face_detection.process(rgb_small)

    if not results.detections:
        return "Neutral", 0.0

    best_emotion    = "Neutral"
    best_confidence = 0.0

    for detection in results.detections:
        bbox = detection.location_data.relative_bounding_box

        # Convert relative coords back to original frame size
        x      = int(bbox.xmin  * w / scale) if scale != 1.0 else int(bbox.xmin  * w)
        y      = int(bbox.ymin  * h / scale) if scale != 1.0 else int(bbox.ymin  * h)
        bw     = int(bbox.width * w / scale) if scale != 1.0 else int(bbox.width  * w)
        bh     = int(bbox.height* h / scale) if scale != 1.0 else int(bbox.height * h)

        x  = max(0, x);  y  = max(0, y)
        bw = min(bw, w - x); bh = min(bh, h - y)

        if bw <= 0 or bh <= 0:
            continue

        face = frame[y:y + bh, x:x + bw]
        if face.size == 0:
            continue

        face = cv2.resize(face, (48, 48))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face = face.astype("float32") / 255.0
        face = face.reshape(1, 48, 48, 1)   # single expand_dims call

        pred       = model.predict(face, verbose=0)
        confidence = float(np.max(pred))
        emotion    = emotion_labels[int(np.argmax(pred))]

        if confidence > best_confidence:
            best_confidence = confidence
            best_emotion    = emotion

    return best_emotion.capitalize(), best_confidence