from transformers import pipeline

class TextEmotionClassifier:
    def __init__(self):
        # We revert to the extremely stable, lightweight public model to fix the backend crash!
        self.classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)
        
        self.emotion_map = {
            "joy": "happy",
            "anger": "angry",
            "sadness": "sad",
            "neutral": "neutral",
            "fear": "fear",
            "surprise": "surprise",
            "disgust": "disgust"
        }

    def predict(self, text: str) -> dict:
        try:
            result = self.classifier(text)[0][0] # Pipeline with top_k=1 returns list of lists
            label = result['label']
            score = result['score']
            
            mapped_emotion = self.emotion_map.get(label, "neutral")
            return {
                "emotion": mapped_emotion,
                "confidence": float(score)
            }
        except Exception as e:
            return {"error": str(e)}
