import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
model = load_model("models/emotion_model.h5")

emotions = ['Angry','Disgust','Fear','Happy','Sad','Surprise','Neutral']

# Test input
sample = np.random.rand(1,48,48,1)

prediction = model.predict(sample)

print("Predicted Emotion:", emotions[np.argmax(prediction)])
