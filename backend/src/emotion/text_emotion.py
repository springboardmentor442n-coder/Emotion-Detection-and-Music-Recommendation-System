from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmotionResult:
    emotion: str
    confidence: float


# Mapping from model labels to project emotions
EMOTION_MAPPING = {
    "joy": "happy",
    "sadness": "sad",
    "anger": "angry",
    "fear": "fearful",
    "surprise": "surprised",
    "disgust": "angry",  # Map disgust to angry
    "neutral": "neutral",
}

# Lazy-loaded emotion classifier
_emotion_classifier = None


def _get_emotion_classifier():
    global _emotion_classifier
    if _emotion_classifier is None:
        try:
            from transformers import pipeline
            _emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True,
            )
        except ImportError:
            raise ImportError("transformers library not installed. Run: pip install transformers torch")
        except Exception as e:
            raise RuntimeError(f"Failed to load emotion model: {e}")
    return _emotion_classifier


# Fallback keyword-based detection
KEYWORDS = {
    "happy": {"happy", "great", "awesome", "excited", "joy", "love"},
    "sad": {"sad", "down", "tired", "cry", "upset", "lonely"},
    "angry": {"angry", "mad", "furious", "annoyed", "rage"},
    "fearful": {"afraid", "scared", "anxious", "nervous", "worry"},
    "surprised": {"wow", "surprised", "unexpected", "shocked"},
    "calm": {"calm", "relaxed", "peaceful", "steady", "quiet"},
}


def _detect_emotion_fallback(text: str) -> EmotionResult:
    lowered = text.lower()
    scores = {emotion: 0 for emotion in KEYWORDS}
    token_count = max(len(lowered.split()), 1)

    for emotion, words in KEYWORDS.items():
        for word in words:
            if word in lowered:
                scores[emotion] += 1

    best_emotion, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return EmotionResult(emotion="neutral", confidence=0.55)

    confidence = min(0.5 + (best_score / token_count), 0.99)
    return EmotionResult(emotion=best_emotion, confidence=round(confidence, 3))


def detect_text_emotion(text: str) -> EmotionResult:
    if not text.strip():
        return EmotionResult(emotion="neutral", confidence=0.5)

    # Temporarily use fallback until model loads properly
    return _detect_emotion_fallback(text)

    # try:
    #     # Try BERT model first
    #     classifier = _get_emotion_classifier()
    #     predictions = classifier(text)

    #     # Find the top emotion
    #     top_emotion = max(predictions[0], key=lambda x: x['score'])
    #     model_label = top_emotion['label'].lower()
    #     confidence = round(top_emotion['score'], 3)

    #     # Map to project emotion
    #     emotion = EMOTION_MAPPING.get(model_label, "neutral")

    #     return EmotionResult(emotion=emotion, confidence=confidence)
    # except Exception:
    #     # Fallback to keyword matching if model fails
    #     return _detect_emotion_fallback(text)
