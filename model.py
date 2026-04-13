import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

nltk.download('stopwords')

df = pd.read_csv("emotion_dataset.csv")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in stopwords.words('english')]
    return " ".join(words)

df['clean_text'] = df['text'].apply(clean_text)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['clean_text'])
y = df['emotion']

model = LogisticRegression()
model.fit(X, y)

def predict_emotion(text):
    text = clean_text(text)
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]