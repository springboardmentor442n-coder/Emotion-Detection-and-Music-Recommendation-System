import pandas as pd
import numpy as np

print("Emotion dataset preprocessing started")

# example loading dataset
data = pd.read_csv("datasets/fer2013.csv")

print(data.head())

print("Dataset loaded successfully")
