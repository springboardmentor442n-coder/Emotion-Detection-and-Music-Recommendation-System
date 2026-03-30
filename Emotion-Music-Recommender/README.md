# MoodMate: Emotion-Detection & Music Recommendation System

## Project Overview
MoodMate is an AI-powered application that detects a user's emotional state through facial expressions or text input and recommends personalized music tracks from a dataset of 57,000+ songs.


## The Problem & Solution
**The Problem:** Traditional music apps recommend songs based on past history, failing to account for the user's immediate emotional state.

**The MoodMate Solution:** Our system uses a **Real-Time Biometric & Sentiment Loop**. Instead of looking at what you liked last week, we look at your face and your words *now*. 
- **CNN Model:** Captured via webcam to detect micro-expressions.
- **NLP Engine:** Analyzes text input for emotional polarity.
- **Result:** A highly personalized, "mood-synced" playlist that improves mental well-being through music therapy.


---

## 📂 Implementation



### Requirements & Data
- **Datasets:** Used FER-2013 for facial expressions and Spotify Million Song Dataset for music.
- **Tech Stack:** Python, TensorFlow, FastAPI, Streamlit.

###  Emotion Detection System
- **Model:** Built a Convolutional Neural Network (CNN).
- **Accuracy:** Trained on 48x48 grayscale images to recognize 6 core emotions (Happy, Sad, Angry, Neutral, Surprise, Fear).
- **Files:** `model.keras`, `image_models.py`.

###  Recommendation Engine
- **Logic:** Implemented a keyword-based mapping system.
- **Integration:** FastAPI backend connects the CNN model to the Music CSV.
- **Output:** Returns JSON data containing Song Title, Artist, and Spotify Search Link.

###  User Interface & Deployment
- **UI:** Developed using Streamlit with three input methods:
  1. **Text Analysis:** Uses Natural Language Processing (NLP).
  2. **Live Camera:** Real-time facial recognition.
  3. **Photo Upload:** Static image analysis.
  
---

## 🛠️ Features

- **Live Camera Detection**: Real-time facial expression analysis using your webcam.
- **Text Sentiment Analysis**: Type how you feel, and the AI will decode your emotion.
- **Spotify Integration**: Instant links to play recommended tracks directly on Spotify.
- **Dynamic UI**: A high-contrast, user-friendly interface designed for clarity and ease of use.



---

## 🛠️ Installation & Setup

   pip install -r frontend/requirements.txt



Run Backend (Terminal 1):

cd backend
python -m uvicorn main:app --reload



Run Frontend (Terminal 2):

cd frontend
streamlit run app.py


---


⚠️ Note on Large Files

Due to GitHub's file size limitations (25MB), the following large files are hosted on Google Drive:

Trained Model (model.keras): Link found in models/Keras-Model_Link.txt

Music Dataset (spotify_millsongdata.csv): Link found in data/spotify_millsongdata.txt

Please download these files and place them in their respective folders before running the application.


---

🎓 Evaluation Criteria Met

Milestone 1: Successful data acquisition and cleaning.

Milestone 2: CNN model with high accuracy on the FER-2013 dataset.

Milestone 3: Seamless integration of emotion classification and music mapping.

Milestone 4: Functional, multi-input UI with real-time testing capabilities.



Developed by: Ishwarya Rani.K
