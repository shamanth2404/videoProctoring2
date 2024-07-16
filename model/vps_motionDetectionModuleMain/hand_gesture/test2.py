import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import TFSMLayer
import os

# Initialize Mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model using TFSMLayer
current_dir = os.path.dirname(__file__)

# Construct the relative path to the model
relative_model_path = os.path.join(current_dir, 'vps_motionDetectionModuleMain', 'hand_gesture', 'mp_hand_gesture')

# Load the model
model = tf.saved_model.load(relative_model_path)

# Read gesture class names
with open('C:\\Users\\shamu\\OneDrive\\Desktop\\aankh\\model\\vps_motionDetectionModuleMain\\hand_gesture\\gesture.names', 'r') as f:
    classNames = f.read().split('\n')

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    x, y, c = frame.shape

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    className = ''
    susflag = ''

    # Post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)
                landmarks.append([lmx, lmy])

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)
            infer = model.signatures['serving_default']
            # Predict gesture
            # landmarks_np = np.array([landmarks], dtype=np.float32)
            landmarks = tf.constant([landmarks], dtype=tf.float32)
            
            prediction = infer(landmarks)
            print(prediction)
            prediction = prediction['dense_16'].numpy()[0]
            classID = np.argmax(prediction)   
            print(classID)         
            className = classNames[classID]
            if className and className != 'fist':
                susflag = 'suspicious'

    # Show the prediction on the frame
    cv2.putText(frame, susflag, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, className, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Show the final output
    cv2.imshow("Output", frame)

    if cv2.waitKey(1) == ord('q'):
        break

# Release the webcam and destroy all active windows
cap.release()
cv2.destroyAllWindows()
