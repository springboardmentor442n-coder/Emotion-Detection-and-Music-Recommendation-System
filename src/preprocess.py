"""
preprocess.py
─────────────
Handles data preprocessing for both:
  1. FER-2013 emotion images  → ready for CNN training
  2. Music CSV                → ready for recommendation engine

Run this script once before training to verify your data is ready.
"""

import os
import numpy as np
import pandas as pd
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — IMAGE PREPROCESSING (for emotion detection)
# ──────────────────────────────────────────────────────────────────────────────

# These are the 7 emotion classes FER-2013 provides
EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

IMG_SIZE = 48  # FER-2013 images are 48×48 pixels


def load_image_for_prediction(image_path: str) -> np.ndarray:
    """
    Load a single image from disk and preprocess it so it can be
    fed directly into the trained CNN model.

    Steps:
      1. Open the image
      2. Convert to grayscale (our CNN expects 1 colour channel)
      3. Resize to 48×48
      4. Normalise pixel values from 0–255 to 0.0–1.0
      5. Add batch & channel dimensions → shape (1, 48, 48, 1)

    Args:
        image_path: Path to any image file (JPG, PNG, etc.)

    Returns:
        numpy array of shape (1, 48, 48, 1) ready for model.predict()
    """
    img = Image.open(image_path).convert("L")   # "L" = grayscale
    img = img.resize((IMG_SIZE, IMG_SIZE))        # resize to 48×48
    img_array = np.array(img, dtype="float32") / 255.0  # normalise
    img_array = img_array.reshape(1, IMG_SIZE, IMG_SIZE, 1)  # add dims
    return img_array


def preprocess_fer_directory(fer_data_dir: str):
    """
    Load ALL images from an FER-2013 folder structure.

    Expected folder layout (standard FER-2013 structure):
        fer_data_dir/
          train/
            angry/
            disgust/
            ...
          test/
            angry/
            ...

    Returns:
        X_train, y_train, X_test, y_test as numpy arrays
    """
    def load_split(split_dir):
        images, labels = [], []
        for label_idx, emotion in enumerate(EMOTION_LABELS):
            emotion_dir = os.path.join(split_dir, emotion)
            if not os.path.exists(emotion_dir):
                print(f"  ⚠️  Folder not found: {emotion_dir} — skipping")
                continue
            files = os.listdir(emotion_dir)
            print(f"  Loading {len(files):5d} images for '{emotion}'")
            for fname in files:
                if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                path = os.path.join(emotion_dir, fname)
                try:
                    img = Image.open(path).convert("L")
                    img = img.resize((IMG_SIZE, IMG_SIZE))
                    arr = np.array(img, dtype="float32") / 255.0
                    images.append(arr)
                    labels.append(label_idx)
                except Exception as e:
                    print(f"    Error loading {path}: {e}")
        return np.array(images), np.array(labels)

    print("\n📂 Loading TRAIN split...")
    X_train, y_train = load_split(os.path.join(fer_data_dir, "train"))
    print("\n📂 Loading TEST split...")
    X_test, y_test = load_split(os.path.join(fer_data_dir, "test"))

    # Reshape for CNN: (N, 48, 48) → (N, 48, 48, 1)
    X_train = X_train.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    X_test  = X_test.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

    print(f"\n✅ Train samples : {len(X_train)}")
    print(f"✅ Test  samples : {len(X_test)}")
    return X_train, y_train, X_test, y_test


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — MUSIC DATA PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────

# Features we'll use for content-based filtering
MUSIC_FEATURES = [
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo",
]


def load_and_clean_music_data(csv_path: str) -> pd.DataFrame:
    """
    Load the music CSV and clean it for the recommendation engine.

    Steps:
      1. Load CSV
      2. Drop rows with missing essential fields
      3. Fill missing audio features with median values
      4. Normalise numeric features to 0–1 range

    Returns:
        Cleaned DataFrame
    """
    print(f"\n🎵 Loading music data from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   Raw rows: {len(df)}")

    # Drop rows where we don't have a track name or artist
    df.dropna(subset=["name", "artist"], inplace=True)

    # Fill missing audio features with column median
    for col in MUSIC_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Fill missing genre
    df["genre"] = df["genre"].fillna("Unknown")

    # Normalise features that aren't already in 0–1
    # loudness is typically -60 to 0 dB → shift to 0–1
    if "loudness" in df.columns:
        df["loudness"] = (df["loudness"] - df["loudness"].min()) / (
            df["loudness"].max() - df["loudness"].min() + 1e-8
        )
    # tempo is BPM (30–250) → normalise
    if "tempo" in df.columns:
        df["tempo"] = (df["tempo"] - df["tempo"].min()) / (
            df["tempo"].max() - df["tempo"].min() + 1e-8
        )

    print(f"   Clean rows: {len(df)}")
    print(f"   Genres    : {sorted(df['genre'].unique())}")
    return df.reset_index(drop=True)


# ──────────────────────────────────────────────────────────────────────────────
# QUICK SELF-TEST
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    # Test music loading
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "music_data.csv")
    if os.path.exists(csv_path):
        df = load_and_clean_music_data(csv_path)
        print("\nSample rows:")
        print(df[["name", "artist", "genre", "valence", "energy"]].head())
    else:
        print(f"Music CSV not found at {csv_path}")

    # Test single-image loading
    print("\n✅ preprocess.py OK")
