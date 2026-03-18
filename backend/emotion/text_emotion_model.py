from transformers import pipeline

# 1. Initialize the pipeline for text classification using the RoBERTa model
emotion_model = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")

# 2. Provide text inputs (as demonstrated in the video)
sentences = [
    "I am not having a good day",  # Video expected: disappointment
    "I'm sorry that I got delayed"  # Video expected: remorse
]

# 3. Get the detected emotions
results = emotion_model(sentences)
print(results)
