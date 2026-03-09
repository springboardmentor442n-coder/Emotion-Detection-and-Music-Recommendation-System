import tensorflow as tf
import numpy as np
from keras.preprocessing.image import ImageDataGenerator

# =========================
# LOAD MODEL
# =========================
model = tf.keras.models.load_model("ml/models/emotion_model.keras")

# =========================
# TEST DATA PATH
# =========================
test_dir = "ml/data/raw/fer2013/test"

# =========================
# DATA GENERATOR
# =========================
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(48,48),
    batch_size=64,
    class_mode='categorical',
    color_mode='grayscale',
    shuffle=False
)

# =========================
# EVALUATE
# =========================
loss, accuracy = model.evaluate(test_data)

print("Test Loss:", loss)
print("Test Accuracy:", accuracy * 100, "%")