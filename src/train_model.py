"""
train_model.py
──────────────
Builds and trains a CNN for emotion detection using FER-2013.

Architecture:
  Input (48×48×1)
  → Conv2D → BatchNorm → MaxPool → Dropout   (×3 blocks)
  → Flatten → Dense → Dropout → Dense (7 classes, softmax)

HOW TO USE:
  1. Download FER-2013 from Kaggle:
     https://www.kaggle.com/datasets/msambare/fer2013
  2. Extract so you have:
     data/fer2013/train/<emotion>/*.png
     data/fer2013/test/<emotion>/*.png
  3. Run:
     python src/train_model.py
  4. Model saves to models/emotion_model.h5
"""

import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# Make sure we can import from sibling modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.preprocess import preprocess_fer_directory, EMOTION_LABELS

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG — tweak these as needed
# ──────────────────────────────────────────────────────────────────────────────
IMG_SIZE    = 48
NUM_CLASSES = 7          # 7 emotions
BATCH_SIZE  = 64
EPOCHS      = 50         # Reduce to 10 for a quick test
LEARNING_RATE = 0.001

BASE_DIR   = os.path.dirname(os.path.dirname(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data", "fer2013")
MODEL_PATH = os.path.join(BASE_DIR, "models", "emotion_model.h5")


# ──────────────────────────────────────────────────────────────────────────────
# MODEL DEFINITION
# ──────────────────────────────────────────────────────────────────────────────
def build_model():
    """
    Build a compact CNN for 48×48 grayscale face images.
    Uses 3 convolutional blocks followed by dense layers.
    """
    model = keras.Sequential([
        # ── Block 1 ──────────────────────────────────────────────
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 1)),

        layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),   # → 24×24×64
        layers.Dropout(0.25),

        # ── Block 2 ──────────────────────────────────────────────
        layers.Conv2D(128, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),   # → 12×12×128
        layers.Dropout(0.25),

        # ── Block 3 ──────────────────────────────────────────────
        layers.Conv2D(256, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),   # → 6×6×256
        layers.Dropout(0.25),

        # ── Classifier ───────────────────────────────────────────
        layers.Flatten(),
        layers.Dense(512, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(NUM_CLASSES, activation="softmax"),  # 7-class output
    ], name="EmotionCNN")

    return model


# ──────────────────────────────────────────────────────────────────────────────
# DATA AUGMENTATION
# ──────────────────────────────────────────────────────────────────────────────
def get_augmentation_layer():
    """
    Light augmentation to make the model more robust.
    Faces can be slightly rotated, shifted, or flipped horizontally.
    """
    return keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),          # ±10 degrees
        layers.RandomZoom(0.1),              # ±10% zoom
        layers.RandomTranslation(0.1, 0.1), # ±10% shift
    ], name="augmentation")


# ──────────────────────────────────────────────────────────────────────────────
# TRAINING
# ──────────────────────────────────────────────────────────────────────────────
def train():
    print("\n" + "═" * 60)
    print("  MoodMate — Emotion Model Training")
    print("═" * 60)

    # 1. Load data
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ FER-2013 data not found at: {DATA_DIR}")
        print("   Please download FER-2013 from Kaggle and extract it there.")
        print("   Expected structure:")
        print(f"   {DATA_DIR}/train/happy/*.png")
        print(f"   {DATA_DIR}/test/happy/*.png")
        return

    X_train, y_train, X_test, y_test = preprocess_fer_directory(DATA_DIR)

    # 2. One-hot encode labels  (e.g. 3 → [0,0,0,1,0,0,0])
    y_train_cat = to_categorical(y_train, NUM_CLASSES)
    y_test_cat  = to_categorical(y_test,  NUM_CLASSES)

    # 3. Build model
    model = build_model()
    model.summary()

    # 4. Augmentation — applied on-the-fly during training
    augment = get_augmentation_layer()

    # 5. Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    # 6. Callbacks
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    callbacks = [
        # Save best model automatically
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        # Reduce LR when validation plateaus
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1,
        ),
        # Stop early if no improvement for 10 epochs
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=10,
            restore_best_weights=True,
            verbose=1,
        ),
        # TensorBoard logs (optional, open with: tensorboard --logdir logs/)
        keras.callbacks.TensorBoard(log_dir="logs/"),
    ]

    # 7. Build tf.data pipelines
    # Training: apply augmentation
    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train_cat))
        .shuffle(len(X_train))
        .batch(BATCH_SIZE)
        .map(lambda x, y: (augment(x, training=True), y),
             num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )
    # Validation: no augmentation
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_test, y_test_cat))
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    # 8. Train!
    print(f"\n🚀 Starting training for up to {EPOCHS} epochs …\n")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
    )

    # 9. Plot & save training curves
    _plot_history(history)

    # 10. Final evaluation
    print("\n🔍 Final evaluation on test set:")
    loss, acc = model.evaluate(val_ds, verbose=0)
    print(f"   Test accuracy : {acc*100:.2f}%")
    print(f"   Test loss     : {loss:.4f}")
    print(f"\n✅ Best model saved to: {MODEL_PATH}")


def _plot_history(history):
    """Save accuracy and loss curves as PNG files."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history.history["accuracy"],     label="Train")
    axes[0].plot(history.history["val_accuracy"], label="Val")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(history.history["loss"],     label="Train")
    axes[1].plot(history.history["val_loss"], label="Val")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    plt.tight_layout()
    plot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "models", "training_curves.png")
    plt.savefig(plot_path)
    print(f"📊 Training curves saved to: {plot_path}")
    plt.close()


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train()
