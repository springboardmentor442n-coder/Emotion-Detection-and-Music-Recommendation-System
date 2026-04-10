# MoodMate Architecture

## High-Level Flow

```mermaid
flowchart TD
    UI[User Interface: Image or Text Input] --> TI[Text Input]
    UI --> FI[Facial Image]

    DS[Dataset Sources] --> FER[FER-2013 Dataset]
    DS --> RAV[RAVDESS Optional]
    DS --> MUSIC[Last.fm or Million Song Subset]

    TI --> ET[Emotion Detection from Text]
    ET --> NLP[NLP Model for Sentiment/Emotion]

    FI --> EI[Emotion Detection from Image]
    FER --> CNN[CNN Model using FER-2013]
    RAV --> CNN
    EI --> CNN

    NLP --> EMO[Detected Emotion]
    CNN --> EMO

    MUSIC --> RE[Music Recommendation Engine]
    EMO --> RE
    RE --> PL[Playlist Generator]
```

## Module View

1. Data collection and preprocessing:
   - FER-2013 image normalization, split handling, augmentation.
   - Last.fm/Million Song cleaning (tags, genre, tempo, mood words).
2. Emotion detection:
   - Text model path (baseline -> BERT/LSTM).
   - Image model path (baseline -> CNN).
3. Recommendation:
   - Emotion-to-tag mapping.
   - Content similarity via TF-IDF + cosine similarity.
4. UI:
   - Upload image / type text.
   - Show detected emotion + ranked tracks.
5. Evaluation:
   - Classification metrics for emotion model.
   - Recommendation precision/coverage and qualitative relevance.
