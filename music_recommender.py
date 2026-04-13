import pandas as pd

df = pd.read_csv("data/song dataset.csv")

def recommend_songs(emotion):
    mapping = {
        "happy": ["happy"],
        "sad": ["sad"],
        "neutral": ["chill"]
    }

    tags = mapping.get(emotion, ["chill"])

    results = df[df['mood'].isin(tags)]

    return results.head(5).to_dict(orient='records')
