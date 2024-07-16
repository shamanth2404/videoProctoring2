import cv2
import mediapipe as mp
import numpy as np
import time
from keras.models import load_model
import pickle
import logging
import dlib
import os

current_dir = os.path.dirname(__file__)


# Configure logging to suppress Mediapipe logging
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Initialize Mediapipe modules
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.2, min_tracking_confidence=0.7)
mp_blazeface = mp.solutions.face_detection
face_detector = mp_blazeface.FaceDetection(min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize dlib for histogram equalization
def apply_histogram_equalization_dlib(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized_gray = dlib.equalize_histogram(gray)
    return cv2.cvtColor(equalized_gray, cv2.COLOR_GRAY2BGR)

# Load the trained model and label encoder
model = load_model(os.path.join(current_dir, 'liveness_model.h5'))
with open(os.path.join(current_dir, 'le.pickle'), "rb") as f:
    le = pickle.load(f)

# Variables for multiple face detection and head pose duration tracking
start_time = None
head_pose_duration_threshold = 60.0  # Threshold for head pose duration (in seconds)
warnings = {}  # Dictionary to store warnings

# Variables for displaying warnings on screen
warning_text = ""
warning_display_time = 0  # Counter for displaying warnings
last_warning_print_time = time.time()

# OpenCV capture initialization
cap = cv2.VideoCapture(0)

# Function to enhance image quality using histogram equalization and adaptive histogram equalization
def enhance_image_quality(image):
    # Convert image to LAB color space for adaptive histogram equalization on the L channel
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Merge the CLAHE enhanced L channel back with A and B channels
    limg = cv2.merge((cl, a, b))

    # Convert LAB image back to BGR color space
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return final

def calculate_head_pose(face_landmarks, image_shape):
    # Extract landmarks and perform head pose calculation
    face_3d = []
    face_2d = []
    img_h, img_w, img_c = image_shape

    for idx, lm in enumerate(face_landmarks.landmark):
        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
            if idx == 1:
                nose_2d = (lm.x * img_w, lm.y * img_h)
                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

            x, y = int(lm.x * img_w), int(lm.y * img_h)

            # Get the 2D Coordinates
            face_2d.append([x, y])

            # Get the 3D Coordinates
            face_3d.append([x, y, lm.z])

    # Convert it to the NumPy array
    face_2d = np.array(face_2d, dtype=np.float64)

    # Convert it to the NumPy array
    face_3d = np.array(face_3d, dtype=np.float64)

    # The camera matrix
    focal_length = 1 * img_w

    cam_matrix = np.array([[focal_length, 0, img_h / 2],
                            [0, focal_length, img_w / 2],
                            [0, 0, 1]])

    # The distortion parameters
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    # Get rotational matrix
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Get angles
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

    # Get the y rotation degree
    x = angles[0] * 360
    y = angles[1] * 360
    z = angles[2] * 360

    return x, y, z

def determine_pose_message(x, y, z):
    # Determine head pose direction based on angles x, y, z
    if y < -10:
        pose_message = "Looking Left"
    elif y > 10:
        pose_message = "Looking Right"
    elif x < -10:
        pose_message = "Looking Down"
    elif x > 20:
        pose_message = "Looking Up"
    else:
        pose_message = "Forward"

    return pose_message

while cap.isOpened():
    success, image = cap.read()

    start = time.time()

    # Apply histogram equalization and CLAHE for enhancing image quality
    image = enhance_image_quality(image)

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)

    # Convert the color space from BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Get results from face detection model
    results = face_mesh.process(image_rgb)

    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Perform face detection using BlazeFace
    num_bounding_boxes = 0
    results_2 = face_detector.process(image)
    if results_2.detections:
        for detection in results_2.detections:
            bounding_box = detection.location_data.relative_bounding_box
            x_min = int(bounding_box.xmin * image.shape[1])
            y_min = int(bounding_box.ymin * image.shape[0])
            width = int(bounding_box.width * image.shape[1])
            height = int(bounding_box.height * image.shape[0])

            # Extract the face region for liveness detection
            face_region = image[y_min:y_min + height, x_min:x_min + width]

            # Ensure the face region is not empty before resizing
            if face_region.size == 0:
                continue

            # Resize and preprocess for liveness detection
            face_region = cv2.resize(face_region, (32, 32))
            face_region = face_region.astype("float") / 255.0
            face_region = np.expand_dims(face_region, axis=0)

            # Perform liveness detection
            preds = model.predict(face_region)[0]
            label = le.classes_[np.argmax(preds)]

            # Skip drawing bounding box for non-live faces
            if label == "non_live":
                continue

            # Draw bounding box for live faces
            cv2.rectangle(image, (x_min, y_min), (x_min + width, y_min + height), (0, 255, 0), 2)
            num_bounding_boxes += 1

        # Display warning for multiple faces detected
        if num_bounding_boxes > 1:
            warning_text = "MULTIPLE FACES DETECTED!"
            cv2.putText(image, warning_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Perform face landmarks detection
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Calculate head pose based on landmarks
            x, y, z = calculate_head_pose(face_landmarks, image.shape)

            # Determine head pose direction message
            pose_message = determine_pose_message(x, y, z)

            # Display head pose direction message
            cv2.putText(image, pose_message, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the processed image with annotations
    cv2.imshow('Face Detection and Head Pose Estimation', image)

    # Check for user input to exit
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
