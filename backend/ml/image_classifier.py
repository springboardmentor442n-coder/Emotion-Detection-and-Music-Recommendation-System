from deepface import DeepFace
import cv2
import numpy as np
import base64

class ImageEmotionClassifier:
    def __init__(self):
        # We don't need to load explicitly here, deepface handles it singleton style
        pass

    def predict_from_base64(self, b64_string: str) -> dict:
        try:
            if "," in b64_string:
                b64_string = b64_string.split(",")[1]
            
            img_data = base64.b64decode(b64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {"error": "Failed to decode image from base64"}

            # Analyze emotion. enforce_detection is false to not crash if face is unclear
            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            
            if isinstance(result, list):
                result = result[0]
                
            dominant_emotion = result.get('dominant_emotion', 'neutral')
            emotion_probs = result.get('emotion', {})
            confidence = emotion_probs.get(dominant_emotion, 0) / 100.0
            
            # Map deepface emotions to our standard set
            emotion_map = {
                "happy": "happy",
                "sad": "sad",
                "angry": "angry",
                "fear": "fear",
                "disgust": "disgust",
                "surprise": "surprise",
                "neutral": "neutral"
            }
            
            mapped_emotion = emotion_map.get(dominant_emotion.lower(), "neutral")
            
            return {
                "emotion": mapped_emotion,
                "confidence": float(confidence)
            }

        except Exception as e:
            print(f"Error in image classification: {str(e)}")
            return {"error": str(e)}
