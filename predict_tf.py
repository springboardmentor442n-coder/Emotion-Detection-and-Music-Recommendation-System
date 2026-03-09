import numpy as np
import cv2
import mediapipe as mp
from keras.models import load_model

# load trained model
model = load_model("ml/models/emotion_model.keras")

# emotion labels (MUST match training order)
emotion_labels = ["angry", "fear", "happy", "neutral", "sad", "surprise"]

# initialize mediapipe face detector
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

# load test image
img = cv2.imread("test.jpg")   # change to your image
h, w, _ = img.shape

# convert to RGB for mediapipe
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# detect faces
results = face_detection.process(rgb)

if results.detections:
    for detection in results.detections:

        bbox = detection.location_data.relative_bounding_box

        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)

        face = img[y:y+height, x:x+width]

        if face.size == 0:
            continue

        # preprocessing (same as training)
        face = cv2.resize(face, (48, 48))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face = face / 255.0
        face = np.reshape(face, (1, 48, 48, 1))

        prediction = model.predict(face)
        label = emotion_labels[np.argmax(prediction)]
        confidence = np.max(prediction) * 100

        print("Emotion:", label)
        print("Confidence:", round(confidence, 2), "%")

        cv2.rectangle(img, (x,y), (x+width,y+height), (255,0,0), 2)
        cv2.putText(img, label, (x,y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()