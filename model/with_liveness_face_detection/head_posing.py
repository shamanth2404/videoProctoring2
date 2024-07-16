
import cv2
import mediapipe as mp
import numpy as np
import time
from keras.models import load_model
import pickle
import logging
import os
logging.getLogger('mediapipe').setLevel(logging.ERROR)


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.2, min_tracking_confidence=0.7)

mp_blazeface = mp.solutions.face_detection
face_detector = mp_blazeface.FaceDetection(min_detection_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

cap = cv2.VideoCapture(0)

print(os.getcwd())

# Load the trained model and label encoder
model = load_model("liveness_model.h5")
with open("le.pickle", "rb") as f:
    le = pickle.load(f)

# Variables for multiple face detection and head pose duration tracking
start_time = None
head_pose_duration_threshold = 60.0  # Threshold for head pose duration (in seconds)
warnings = {}  # Dictionary to store warnings

# Variables for displaying warnings on screen
warning_text = ""
warning_display_time = 0  # Counter for displaying warnings
display_warning = False  # Flag to control warning display
last_warning_print_time = time.time()

while cap.isOpened():
    success, image = cap.read()

    start = time.time()

    # Flip the image horizontally for a later selfie-view display
    # Also convert the color space from BGR to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance
    image.flags.writeable = False

    # Get the result
    results = face_mesh.process(image)

    # To improve performance
    image.flags.writeable = True

    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []

    num_bounding_boxes = 0
    success_2, image = cap.read()
    if not success_2:
        break
    results_2 = face_detector.process(image)

    if results_2.detections:
        
        # Draw a bounding box around each face
        for detection in results_2.detections:
            bounding_box = detection.location_data.relative_bounding_box
            x_min = int(bounding_box.xmin * img_w)
            y_min = int(bounding_box.ymin * img_h)
            width = int(bounding_box.width * img_w)
            height = int(bounding_box.height * img_h)
            # Extract the face region for liveness detection
            face_region = image[y_min:y_min + height, x_min:x_min + width]

            # Ensure the face region is not empty before resizing
            if face_region.size == 0:
                continue


           

            face_region = cv2.resize(face_region, (32, 32))
            face_region = face_region.astype("float") / 255.0
            face_region = np.expand_dims(face_region, axis=0)

            

            
            
            
            

            # Perform liveness detection
            preds = model.predict(face_region)[0]
            # print("preds")
            # print(preds)
            label = le.classes_[np.argmax(preds)]

            # If the face is predicted as non-live, skip drawing bounding box
            if label == "non_live":
                continue

            # Draw bounding box for live faces
            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_min + width), int(y_min + height)), (0, 255, 0), 2)
            num_bounding_boxes += 1

        if num_bounding_boxes > 1:
            print("More than one face detected!")
            warning_text = "MULTIPLE FACES DETECTED!"
            image_height, image_width = image.shape[:2]
            text_x = image_width - 500
            text_y = 50
            cv2.putText(image, warning_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
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

            # See where the user's head tilting
            if y < -10:
                pose = "Looking Left"
            elif y > 10:
                pose = "Looking Right"
            elif x < -10:
                pose = "Looking Down"
            elif x > 20:
                pose = "Looking Up"
            else:
                pose = "Forward"

            # Display the nose direction
            nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))

            # Add the text on the image
            cv2.putText(image, pose, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(image, "x: " + str(np.round(x, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "y: " + str(np.round(y, 2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "z: " + str(np.round(z, 2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Check for warnings and store them as objects in the dictionary
            if pose != "Forward":
                if pose not in warnings:
                    warnings[pose] = [{"count": 1, "start_time": time.time(), "duration": 0.0}]
                else:
                    # Update previous duration
                    if len(warnings[pose]) > 0:
                        warnings[pose][-1]["duration"] += time.time() - warnings[pose][-1]["start_time"]
                    warnings[pose].append({"count": 1, "start_time": time.time(), "duration": 0.0})

            # Check for expired warnings and print them
            for pose, entries in warnings.items():
                total_duration = sum(entry["duration"] for entry in entries)
                if total_duration >= head_pose_duration_threshold:
                    if time.time() - last_warning_print_time > 5:
                        print(f"Warning: {pose} pose detected for more than {total_duration:.1f} seconds")
                        last_warning_print_time = time.time()
                        warning_text = f"{pose} pose detected for more than {total_duration:.1f} seconds"
                        warning_display_time = 5  # Display warning for 5 seconds

    else:
        start_time = None
    
    #print("Face region dimensions:", face_region.shape)
    
    # mp_drawing.draw_landmarks(
    #                 image=image,
    #                 landmark_list=face_landmarks,
    #                 connections=mp_face_mesh.FACEMESH_CONTOURS,
    #                 landmark_drawing_spec=drawing_spec,
    #                 connection_drawing_spec=drawing_spec
    #                 )

    cv2.imshow('Face Detection', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
