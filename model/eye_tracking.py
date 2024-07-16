import cv2 as cv
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

# left eyes indices
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
# right eyes indices
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

# irises Indices list
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

cap = cv.VideoCapture(0)

with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
) as face_mesh:

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv.flip(frame, 1)

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(rgb_frame)
        mask = np.zeros((img_h, img_w), dtype=np.uint8)

        if results.multi_face_landmarks:

            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])

            left_eye_center = np.mean(mesh_points[LEFT_EYE], axis=0).astype(int)
            right_eye_center = np.mean(mesh_points[RIGHT_EYE], axis=0).astype(int)

            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)

            # Draw circles on the frame
            cv.circle(frame, center_left, int(l_radius), (0, 255, 0), 2, cv.LINE_AA)
            cv.circle(frame, center_right, int(r_radius), (0, 255, 0), 2, cv.LINE_AA)

            # Display coordinates as text
            cv.putText(frame, f'Left Iris: ({l_cx}, {l_cy})', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1,
                       cv.LINE_AA)
            cv.putText(frame, f'Right Iris: ({r_cx}, {r_cy})', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1,
                       cv.LINE_AA)

            # Calculate the average horizontal position of both irises
            avg_iris_position = (l_cx + r_cx) / 2

            # Calculate the average horizontal position of both eyes
            avg_eye_position = (left_eye_center[0] + right_eye_center[0]) / 2

            # Determine overall gaze direction
            gaze_direction = "Center"
            if avg_iris_position < avg_eye_position:
                gaze_direction = "Right"
            elif avg_iris_position > avg_eye_position:
                gaze_direction = "Left"

            # Display gaze direction as text
            cv.putText(frame, f'Overall Gaze Direction: {gaze_direction}', (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1, cv.LINE_AA)

            # Drawing on the mask
            cv.circle(mask, center_left, int(l_radius), (255, 255, 255), -1, cv.LINE_AA)
            cv.circle(mask, center_right, int(r_radius), (255, 255, 255), -1, cv.LINE_AA)

        cv.imshow('Mask', mask)
        cv.imshow('img', frame)
        key = cv.waitKey(1)
        if key == ord('q'):
            break
cap.release()
cv.destroyAllWindows()