from flask import Flask, request, jsonify
import cv2 as cv
import numpy as np
from flask_cors import CORS
import mediapipe as mp
from io import BytesIO
from PIL import Image
import time
from pymongo import MongoClient
# app = Flask(__name__)
# CORS(app)

client = MongoClient('mongodb+srv://shamanthk2404:Shamanthk2404@cluster0.bgsebd6.mongodb.net/videoProctoring?retryWrites=true&w=majority&appName=Cluster0')
db = client['videoProctoring']
collection = db['direction_data']

mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

def get_user_data(email):
    user_data = collection.find_one({"email": email})
    if user_data:
        return {
            "last_gaze_direction": user_data.get("last_eye_direction", "Center"),
            "gaze_start_time": user_data.get("eye_start_time", time.time())
        }
    else:
        return {
            "last_gaze_direction": "Center",
            "gaze_start_time": time.time()
        }
def update_user_data(email, last_gaze_direction, gaze_start_time):
    collection.update_one(
        {"email": email},
        {"$set": {"last_eye_direction": last_gaze_direction, "last_eye_time": gaze_start_time}},
        upsert=True
    )

def process_image(image,email):   
    try:
        user_data = get_user_data(email)
        last_gaze_direction = user_data["last_gaze_direction"]
        gaze_start_time = float(user_data["gaze_start_time"])
    except Exception as e:
        print(f"Error :{e}")
        


    with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    ) as face_mesh:
        rgb_frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        img_h, img_w = image.shape[:2]
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])

            left_eye_center = np.mean(mesh_points[LEFT_EYE], axis=0).astype(int)
            right_eye_center = np.mean(mesh_points[RIGHT_EYE], axis=0).astype(int)

            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)

            avg_iris_position = (l_cx + r_cx) / 2
            avg_eye_position = (left_eye_center[0] + right_eye_center[0]) / 2

            gaze_direction = "Center"
            if avg_iris_position < avg_eye_position:
                gaze_direction = "Right"
            elif avg_iris_position > avg_eye_position:
                gaze_direction = "Left"

            current_time = time.time()
            if gaze_direction != last_gaze_direction:
                print(gaze_direction,last_gaze_direction)
                update_user_data(email, gaze_direction, current_time)
            else:
                # Check if gaze direction has been the same for more than 5 seconds
                print(gaze_direction,current_time,gaze_start_time)
                if gaze_direction != "Center":
                    print(gaze_direction,current_time,gaze_start_time)
                    update_user_data(email, gaze_direction, current_time)
                    return {
                        "warning": f"Student looking aside for more than 5 seconds"
                    }

            update_user_data(email, gaze_direction, gaze_start_time)

            return {
                "left_iris": (l_cx, l_cy),
                "right_iris": (r_cx, r_cy),
                "gaze_direction": gaze_direction
            }
        return {"message": "No face detected"}



