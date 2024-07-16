import cv2
import numpy as np
import math
from face_detector import get_face_detector, find_faces
from face_landmarks import get_landmark_model, detect_marks, draw_marks
from _thread import *
import psycopg2
from flask import Flask, render_template, request, abort, redirect, url_for, session, Response
from flask_session import Session
import time
from pymongo import MongoClient

__all__ = ("error", "LockType", "start_new_thread", "interrupt_main", "exit", "allocate_lock", "get_ident", "stack_size", "acquire", "release", "locked")
  

client = MongoClient('mongodb+srv://shamanthk2404:Shamanthk2404@cluster0.bgsebd6.mongodb.net/videoProctoring?retryWrites=true&w=majority&appName=Cluster0')
db = client['videoProctoring']
collection = db['direction_data']

def eye_on_mask(mask, side, shape):
 
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    l = points[0][0]
    t = (points[1][1]+points[2][1])//2
    r = points[3][0]
    b = (points[4][1]+points[5][1])//2
    return mask, [l, t, r, b]

def find_eyeball_position(end_points, cx, cy):
    """Find and return the eyeball positions, i.e. left or right or top or normal"""
    x_ratio = (end_points[0] - cx)/(cx - end_points[2])
    y_ratio = (cy - end_points[1])/(end_points[3] - cy)
    if x_ratio > 3:
        return 1
    elif x_ratio < 0.33:
        return 2
    elif y_ratio < 0.33:
        return 3
    else:
        return 0

    
def contouring(thresh, mid, img, end_points, right=False):
    gray_thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY) if thresh.ndim == 3 else thresh
 
    cnts, _ = cv2.findContours(gray_thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        pos = find_eyeball_position(end_points, cx, cy)
        return pos
    except:
        pass
    
def process_thresh(thresh):
 
    thresh = cv2.erode(thresh, None, iterations=2) 
    thresh = cv2.dilate(thresh, None, iterations=4) 
    thresh = cv2.medianBlur(thresh, 3) 
    thresh = cv2.bitwise_not(thresh)
    return thresh

# def print_eye_pos(img, left, right):
 
#     if left == right and left != 0:
#         text = ''
        
#         connection = psycopg2.connect(user="postgres",
#                                           password="Shamanth",
#                                           host="localhost",
#                                           port="5432",
#                                           database="proctoring")
#         cursor = connection.cursor()
        
#         if left == 1:
#             print('Looking left')
#             text = 'Looking left'
#         elif left == 2:
#             print('Looking right')
#             text = 'Looking right'
#         elif left == 3:
#             print('Looking up')
#             text = 'Looking up'
#         else:
#             print('Nothing')
#         font = cv2.FONT_HERSHEY_SIMPLEX 
#         cv2.putText(img, text, (30, 30), font,  
#                    1, (0, 255, 255), 2, cv2.LINE_AA) 
        
 
def get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val):
    """Return the 3D points present as 2D for making annotation box"""
    point_3d = []
    dist_coeffs = np.zeros((4,1))
    rear_size = val[0]
    rear_depth = val[1]
    point_3d.append((-rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, -rear_size, rear_depth))
    
    front_size = val[2]
    front_depth = val[3]
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d.append((-front_size, front_size, front_depth))
    point_3d.append((front_size, front_size, front_depth))
    point_3d.append((front_size, -front_size, front_depth))
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d = np.array(point_3d, dtype=np.float64).reshape(-1, 3)
    
    # Map to 2d img points
    (point_2d, _) = cv2.projectPoints(point_3d,
                                      rotation_vector,
                                      translation_vector,
                                      camera_matrix,
                                      dist_coeffs)
    point_2d = np.int32(point_2d.reshape(-1, 2))
    return point_2d

def draw_annotation_box(img, rotation_vector, translation_vector, camera_matrix,
                        rear_size=300, rear_depth=0, front_size=500, front_depth=400,
                        color=(255, 255, 0), line_width=2):
 
    
    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size*2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    # # Draw all the lines
    cv2.polylines(img, [point_2d], True, color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[1]), tuple(
        point_2d[6]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[2]), tuple(
        point_2d[7]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[3]), tuple(
        point_2d[8]), color, line_width, cv2.LINE_AA)
    
    
def head_pose_points(img, rotation_vector, translation_vector, camera_matrix):
  
    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size*2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    y = (point_2d[5] + point_2d[8])//2
    x = point_2d[2]
    
    return (x, y)

face_model = get_face_detector()
landmark_model = get_landmark_model()
left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]




kernel = np.ones((9, 9), np.uint8)
 

font = cv2.FONT_HERSHEY_SIMPLEX 

outer_points = [[49, 59], [50, 58], [51, 57], [52, 56], [53, 55]]
d_outer = [0]*5
inner_points = [[61, 67], [62, 66], [63, 65]]
d_inner = [0]*3
 
d_outer[:] = [x / 100 for x in d_outer]
d_inner[:] = [x / 100 for x in d_inner] 

# 3D model points.
model_points = np.array([
                            (0.0, 0.0, 0.0),             # Nose tip
                            (0.0, -330.0, -65.0),        # Chin
                            (-225.0, 170.0, -135.0),     # Left eye left corner
                            (225.0, 170.0, -135.0),      # Right eye right corne
                            (-150.0, -150.0, -125.0),    # Left Mouth corner
                            (150.0, -150.0, -125.0)      # Right mouth corner
                        ])

# Camera internals


def nothing(x):
    pass

countpr = 0
counth = 0

def get_user_data(email):
    user_data = collection.find_one({"email": email})
    if user_data:
        return {
            "last_mouth_direction": user_data.get("last_mouth_direction", "Center"),
            "gaze_start_time": user_data.get("mouth_start_time", time.time())
        }
    else:
        return {
            "last_mouth_direction": "Center",
            "gaze_start_time": time.time()
        }
def update_user_data(email, last_gaze_direction, gaze_start_time):
    collection.update_one(
        {"email": email},
        {"$set": {"last_mouth_direction": last_gaze_direction, "last_mouth_time": gaze_start_time}},
        upsert=True
    )


def mouth_track(img,email):
    try:
        user_data = get_user_data(email)
        last_mouth_direction = user_data["last_mouth_direction"]
        mouth_start_time = float(user_data["gaze_start_time"])
    except Exception as e:
        print(f"Error :{e}")

    thresh = img.copy()
    rects = find_faces(img, face_model)
    
    for rect in rects:
        shape = detect_marks(img, landmark_model, rect)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask, end_points_left = eye_on_mask(mask, left, shape)
        mask, end_points_right = eye_on_mask(mask, right, shape)
        mask = cv2.dilate(mask, kernel, 5)
        
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = int((shape[42][0] + shape[39][0]) // 2)
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        
        thresh = process_thresh(thresh)
        
        eyeball_pos_left = contouring(thresh[:, 0:mid], mid, img, end_points_left)
        eyeball_pos_right = contouring(thresh[:, mid:], mid, img, end_points_right, True)
        
        # for (x, y) in shape[36:48]:
        #     cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
        shape = detect_marks(img, landmark_model, rect)
        cnt_outer = 0
        cnt_inner = 0
        draw_marks(img, shape[48:])
        for i, (p1, p2) in enumerate(outer_points):
            print(p1,p2,shape[p2][1] , shape[p1][1])
            if d_outer[i] + 3 < shape[p2][1] - shape[p1][1]:
                print(p1,p2,shape[p2][1] , shape[p1][1])
                cnt_outer += 1 
        for i, (p1, p2) in enumerate(inner_points):
            print(p1,p2, shape[p2][1] , shape[p1][1])
            if d_inner[i] + 2 <  shape[p2][1] - shape[p1][1]:                
                cnt_inner += 1
        current_time = time.time()

        if cnt_outer > 3 and cnt_inner > 2:
            mouth_direction = "Mouth Open"
            print(cnt_outer, cnt_inner)
            print(mouth_direction)
            
            if mouth_direction != last_mouth_direction:
                last_mouth_direction = mouth_direction
                mouth_start_time = current_time
                update_user_data(email, mouth_direction, current_time)
            else:
                # Check if mouth direction has been the same for more than 5 seconds
                
                    
                    update_user_data(email, mouth_direction, current_time)
                    return {
                        "warning": "Student Mouth Open for more than 5 seconds"
                    }

            update_user_data(email, mouth_direction, mouth_start_time)
            return {
                "result": mouth_direction
            }
        else:
            mouth_direction = "Mouth Close"
            print(cnt_outer, cnt_inner)
            print(mouth_direction)
            last_mouth_direction = mouth_direction
            update_user_data(email, mouth_direction, current_time)
            return {
                "result": mouth_direction
            }
            # sql_decrease_query = """UPDATE proctoring SET count = count - 10 WHERE username=username;"""
            # cursor.execute(sql_decrease_query)
            # connection.commit()            
        # show the output image with the face detections + facial landmarks
    
    

 
