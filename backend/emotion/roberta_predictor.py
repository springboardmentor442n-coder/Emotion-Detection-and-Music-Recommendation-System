"""
RoBERTa-based text emotion predictor for MoodMate.

Uses the SamLowe/roberta-base-go_emotions pipeline for emotion detection.
Maps GoEmotions labels to MoodMate's 6 emotion classes.
"""
import torch
from transformers import pipeline

# Emotion label order as per project spec
EMOTION_LABELS = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Mapping from GoEmotions labels → MoodMate's 6 emotion classes
GO_EMOTIONS_TO_MOODMATE = {
    'anger': 'angry',
    'annoyance': 'angry',
    'disapproval': 'angry',
    'disgust': 'angry',
    'fear': 'fear',
    'nervousness': 'fear',
    'joy': 'happy',
    'amusement': 'happy',
    'approval': 'happy',
    'excitement': 'happy',
    'gratitude': 'happy',
    'love': 'happy',
    'optimism': 'happy',
    'pride': 'happy',
    'relief': 'happy',
    'admiration': 'happy',
    'desire': 'happy',
    'caring': 'happy',
    'neutral': 'neutral',
    'realization': 'neutral',
    'curiosity': 'neutral',
    'confusion': 'neutral',
    'sadness': 'sad',
    'disappointment': 'sad',
    'grief': 'sad',
    'remorse': 'sad',
    'embarrassment': 'sad',
    'surprise': 'surprise',
}

# Load model once at module level to avoid reloading on every request
_emotion_pipeline = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions"
)


def predict_emotion(text: str) -> str:
    """
    Predict the emotion of a given text input.

    Args:
        text: The input text string to classify.

    Returns:
        One of the 6 MoodMate emotion labels:
        'angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'
    """
    result = _emotion_pipeline(text)
    go_emotion_label = result[0]['label']

    # Map the GoEmotions label to MoodMate's 6 classes
    emotion = GO_EMOTIONS_TO_MOODMATE.get(go_emotion_label, 'neutral')
    return emotion


if __name__ == "__main__":
    # Quick test
    test_sentences = [
        "I am not having a good day",
        "I'm sorry that I got delayed",
        "This is absolutely amazing!",
        "I don't know what to think about this",
        "That really scared me",
        "Wow I didn't expect that at all",
    ]
    for sentence in test_sentences:
        emotion = predict_emotion(sentence)
        print(f"Text: {sentence!r}  →  Emotion: {emotion}")
