import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv("data/emotion_dataset.csv")

print("DATASET:")
print(df)

print("\nLABEL COUNT:")
print(df["emotion"].value_counts())

X = df["text"]
y = df["emotion"]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X_vec = vectorizer.fit_transform(X)

model = LogisticRegression(max_iter=200)
model.fit(X_vec, y)

y_pred = model.predict(X_vec)

accuracy = accuracy_score(y, y_pred)
print("\nModel Accuracy:", accuracy)

def predict_emotion(text):
    text_vec = vectorizer.transform([text])
    return model.predict(text_vec)[0]