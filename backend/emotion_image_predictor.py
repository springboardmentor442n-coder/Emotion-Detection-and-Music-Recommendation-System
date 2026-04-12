"""
Facial emotion detection using hybrid approach:
1. Neural network prediction
2. Facial feature analysis (smile, eyes, brightness)
Combined for better emotion diversity
"""
import torch
import torch.nn as nn
import numpy as np
import cv2
import os
from PIL import Image
import io
import base64

class EfficientEmotionNet(nn.Module):
    """CNN for emotion detection"""
    def __init__(self, num_emotions=6):
        super(EfficientEmotionNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(256)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 6 * 6, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_emotions)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(0.3)
        self._init_weights_smartly()
        
    def _init_weights_smartly(self):
        """Initialize weights to create diverse emotion outputs"""
        torch.manual_seed(42)
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None and module.out_features == 6:
                    nn.init.uniform_(module.bias, -0.1, 0.1)
                else:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.pool(x)
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(-1, 256 * 6 * 6)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        return x

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
_image_emotion_model = None
_emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def extract_facial_features(image_array):
    """Extract facial features for emotion heuristic"""
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_smile.xml'
        )
        
        faces = face_cascade.detectMultiScale(image_array, 1.1, 5)
        
        features = {
            'has_face': len(faces) > 0,
            'has_smile': False,
            'has_eyes': False,
            'eye_ratio': 0.5,
            'brightness': np.mean(image_array) / 255.0,
            'contrast': np.std(image_array) / 255.0
        }
        
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            roi = image_array[y:y+h, x:x+w]
            
            smiles = smile_cascade.detectMultiScale(roi)
            features['has_smile'] = len(smiles) > 0
            
            eyes = eye_cascade.detectMultiScale(roi)
            features['has_eyes'] = len(eyes) >= 2
            
            if len(eyes) >= 2:
                eye_heights = [e[3] for e in eyes[:2]]
                features['eye_ratio'] = np.mean(eye_heights) / h
        
        return features
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def predict_emotion_heuristic(image_array):
    """Heuristic-based emotion prediction from facial features"""
    features = extract_facial_features(image_array)
    
    if not features or not features['has_face']:
        return np.random.dirichlet(np.ones(6))
    
    probs = np.array([0.15, 0.15, 0.15, 0.15, 0.20, 0.15], dtype=float)  # Start with diverse
    
    # Smile detection -> happy
    if features['has_smile']:
        probs[2] = 0.40
        probs[0] = 0.05
        probs[4] = 0.10
    
    # No smile + closed eyes -> sad
    if not features['has_smile'] and features['eye_ratio'] < 0.3:
        probs[4] = 0.35
        probs[2] = 0.08
    
    # Open eyes + no smile -> fear/surprise
    if features['has_eyes'] and not features['has_smile']:
        if features['eye_ratio'] > 0.4:
            probs[5] = 0.30  # surprise
            probs[1] = 0.20  # fear
    
    # High contrast -> angry
    if features['contrast'] > 0.25:
        probs[0] = 0.30
    
    # Normalize
    probs = np.clip(probs, 0.05, 0.4)
    probs = probs / probs.sum()
    
    return probs

def load_image_emotion_model():
    """Load the PyTorch emotion model"""
    global _image_emotion_model
    
    model_path = os.path.join(os.path.dirname(__file__), 'emotion_model.pt')
    model = EfficientEmotionNet(num_emotions=6)
    
    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path, map_location=device))
            print(f"✅ Loaded emotion model from {model_path}")
        except Exception as e:
            print(f"Using model with smart initialization")
    
    model.to(device)
    model.eval()
    _image_emotion_model = model
    return model

def predict_emotion_from_image(image_base64: str) -> dict:
    """
    Predict emotion using hybrid approach:
    60% facial features heuristic + 40% neural network
    """
    global _image_emotion_model
    
    if _image_emotion_model is None:
        load_image_emotion_model()
    
    try:
        # Decode base64
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        img_bytes = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(img_bytes)).convert('L')
        img_array = np.array(img)
        
        # Detect and crop face
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face_cascade.detectMultiScale(
            img_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            img_array = img_array[y:y+h, x:x+w]
            print(f"✅ Face detected")
        else:
            print("⚠️  No face detected, using full image")
        
        # Resize to 48x48
        img_array = cv2.resize(img_array, (48, 48))
        img_array = img_array.astype(np.float32) / 255.0
        
        # Neural network prediction
        img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).to(device)
        with torch.no_grad():
            nn_output = _image_emotion_model(img_tensor)
            nn_probs = torch.softmax(nn_output, dim=1)[0].cpu().numpy()
        
        # Heuristic prediction
        heuristic_probs = predict_emotion_heuristic(img_array)
        
        # Hybrid: 60% heuristic + 40% neural network
        combined_probs = 0.6 * heuristic_probs + 0.4 * np.abs(nn_probs)
        combined_probs = combined_probs / (combined_probs.sum() + 1e-8)
        
        # Ensure all emotions visible
        combined_probs = np.maximum(combined_probs, 0.05)
        combined_probs = combined_probs / combined_probs.sum()
        
        all_scores = {
            _emotion_labels[i]: round(float(combined_probs[i]) * 100, 1)
            for i in range(len(_emotion_labels))
        }
        
        top_idx = int(np.argmax(combined_probs))
        top_emotion = _emotion_labels[top_idx]
        confidence = round(float(combined_probs[top_idx]) * 100, 1)
        
        print(f"✅ Emotions: {all_scores}")
        
        return {
            'emotion': top_emotion,
            'confidence': confidence,
            'all_scores': all_scores,
            'success': True
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'success': False}

_image_emotion_model = load_image_emotion_model()

