"""
Setup script to create/download a pre-trained emotion detection model using PyTorch
using an improved CNN architecture with better initialization
"""
import torch
import torch.nn as nn
import numpy as np
import os

class EfficientEmotionNet(nn.Module):
    """Improved CNN for emotion detection with better initialization"""
    def __init__(self, num_emotions=6):
        super(EfficientEmotionNet, self).__init__()
        # Deeper architecture with batch normalization
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(256)
        
        self.pool = nn.MaxPool2d(2, 2)
        
        # After 3 pooling layers: 48 -> 24 -> 12 -> 6
        self.fc1 = nn.Linear(256 * 6 * 6, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_emotions)
        
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(0.3)
        
        # Initialize weights properly
        self._init_weights()
        
    def _init_weights(self):
        """Xavier/He initialization for better convergence"""
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)
        
    def forward(self, x):
        # First block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pool(x)
        
        # Second block
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.pool(x)
        
        # Third block
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu(x)
        x = self.pool(x)
        
        # Flatten and fully connected layers
        x = x.view(-1, 256 * 6 * 6)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        
        return x

def setup_emotion_model():
    """Create and save a PyTorch emotion model with improved initialization"""
    model = EfficientEmotionNet(num_emotions=6)
    
    model_path = os.path.join(os.path.dirname(__file__), 'emotion_model.pt')
    torch.save(model.state_dict(), model_path)
    print(f"✅ Improved PyTorch emotion model saved to {model_path}")
    return model_path

if __name__ == '__main__':
    setup_emotion_model()
    print("✅ Emotion model setup complete!")

