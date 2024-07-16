from flask import Flask, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import time

app = Flask(__name__)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

mp_blazeface = mp.solutions.face_detection
face_detector = mp_blazeface.FaceDetection(min_detection_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Variables for multiple face detection and head pose duration tracking
start_time = time.time()
head_pose_duration_threshold = 60.0  # Threshold for head pose duration (in seconds)
warnings = {}  # Dictionary to store warnings
last_warning_print_time = time.time()
pose_start_time = time.time()
last_pose = "Forward"
def process_image(image):
    global start_time, warnings, last_warning_print_time, pose_start_time, last_pose

    warning_text = ""
    pose = ""
    # Convert the color space from BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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
    results_2 = face_detector.process(image)

    if results_2.detections:
        for detection in results_2.detections:
            bounding_box = detection.location_data.relative_bounding_box
            x_min = bounding_box.xmin * image.shape[1]
            y_min = bounding_box.ymin * image.shape[0]
            width = bounding_box.width * image.shape[1]
            height = bounding_box.height * image.shape[0]

            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_min + width), int(y_min + height)), (0, 255, 0), 2)
            num_bounding_boxes += 1

        if num_bounding_boxes > 1:
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

            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)

            focal_length = 1 * img_w
            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            rmat, jac = cv2.Rodrigues(rot_vec)
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

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

            nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)
            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))

            cv2.putText(image, pose, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(image, "x: " + str(np.round(x, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "y: " + str(np.round(y, 2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "z: " + str(np.round(z, 2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # if pose != "Forward":
            #     if pose not in warnings:
            #         warnings[pose] = [{"count": 1, "start_time": time.time(), "duration": 0.0}]
            #     else:
            #         if len(warnings[pose]) > 0:
            #             warnings[pose][-1]["duration"] += time.time() - warnings[pose][-1]["start_time"]
            #         warnings[pose].append({"count": 1, "start_time": time.time(), "duration": 0.0})

            # for pose, entries in warnings.items():
            #     total_duration = sum(entry["duration"] for entry in entries)
            #     if total_duration >= head_pose_duration_threshold:
            #         if time.time() - last_warning_print_time > 5:
            #             warning_text = f"{pose} pose detected for more than {total_duration:.1f} seconds"
            #             last_warning_print_time = time.time()

    image_list = image.tolist()

    current_time = time.time()
    if pose != last_pose:
        last_pose = pose
        pose_start_time = current_time
    else:
        # Check if gaze direction has been the same for more than 5 seconds
        if (pose != "Forward" or pose != "Looking Up") and (current_time - gaze_start_time) > 5:
            last_pose = ""
            return {
                "warning": f"Student {last_pose} for more than 5 seconds"
            }
    
    return pose




