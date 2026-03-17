import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from emotion_model import create_model

print("Loading dataset...")

data = pd.read_csv("datasets/fer2013.csv")

X = []
for pixel in data['pixels']:
    img = np.array(pixel.split(), dtype='float32').reshape(48,48,1)
    X.append(img)

X = np.array(X) / 255.0
y = to_categorical(data['emotion'], 7)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = create_model()

print("Training started...")
model.fit(X_train, y_train, epochs=3, batch_size=64)

loss, acc = model.evaluate(X_test, y_test)
print("Accuracy:", acc)

model.save("models/emotion_model.h5")
