from __future__ import annotations

import io
from typing import Any

import numpy as np
from PIL import Image


def detect_image_emotion(image_bytes: bytes) -> dict[str, Any]:
    """
    Detect emotion from image using DeepFace library.
    Falls back to OpenCV-based detection if DeepFace is unavailable.
    """
    try:
        from deepface import DeepFace
        
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Ensure 3-channel image (RGB)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
        
        # Detect emotions using DeepFace
        result = DeepFace.analyze(
            img_array,
            actions=['emotion'],
            enforce_detection=False,
            silent=True
        )
        
        if result and len(result) > 0:
            emotions_dict = result[0].get('emotion', {})
            
            if emotions_dict:
                # Get dominant emotion
                dominant_emotion = max(emotions_dict.items(), key=lambda x: x[1])
                emotion_name = dominant_emotion[0]
                score = dominant_emotion[1] / 100  # Convert to 0-1 scale
                
                # Map to project emotions
                emotion_map = {
                    'happy': 'happy',
                    'sad': 'sad',
                    'angry': 'angry',
                    'fear': 'fearful',
                    'surprise': 'surprised',
                    'disgust': 'angry',
                    'neutral': 'neutral'
                }
                
                final_emotion = emotion_map.get(emotion_name, 'neutral')
                
                return {
                    "emotion": final_emotion,
                    "confidence": round(float(score), 3),
                    "analysis": f"Detected {final_emotion} emotion with score {score:.1%} using DeepFace model.",
                }
        
        # If no face detected, return neutral
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "analysis": "No clear emotion detected in image (possibly no face or unclear expression).",
        }
        
    except (ImportError, Exception) as e:
        # Fallback: Try with OpenCV if DeepFace not available
        try:
            import cv2
            
            # Load cascade classifier
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert bytes to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "emotion": "neutral",
                    "confidence": 0.5,
                    "analysis": "Failed to load image.",
                }
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {
                    "emotion": "neutral",
                    "confidence": 0.5,
                    "analysis": "No face detected in image.",
                }
            
            # Face detected - return calm as default for OpenCV fallback
            # (since OpenCV doesn't have emotion detection built-in)
            return {
                "emotion": "calm",
                "confidence": 0.65,
                "analysis": f"Face detected in image ({len(faces)} face(s)). Use OpenAI API for accurate emotion detection.",
            }
            
        except (ImportError, Exception):
            # Final fallback: Return neutral
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "analysis": "Please configure OPENAI_API_KEY for accurate emotion detection. Install 'deepface' for local detection: pip install deepface",
            }
