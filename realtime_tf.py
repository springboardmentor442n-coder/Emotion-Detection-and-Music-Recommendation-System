import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model

# Load emotion model
model = load_model("ml/models/emotion_model.keras")

emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Initialize MediaPipe face detector
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # Convert BGR → RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    results = face_detection.process(rgb)

    if results.detections:
        for detection in results.detections:

            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)

            face = frame[y:y+height, x:x+width]

            if face.size == 0:
                continue

            # Preprocess face
            face = cv2.resize(face, (48,48))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            face = face / 255.0
            face = np.reshape(face, (1,48,48,1))

            pred = model.predict(face, verbose=0)
            emotion = emotion_labels[np.argmax(pred)]

            # Draw rectangle and label
            cv2.rectangle(frame,(x,y),(x+width,y+height),(0,255,0),2)
            cv2.putText(frame,emotion,(x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,0),2)

    cv2.imshow("Emotion Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()