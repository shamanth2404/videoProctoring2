from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import math
import base64

app = Flask(__name__)

# model
model = YOLO("yolo-Weights/yolov8n.pt")

# object classes
classNames = ["person", "backpack", "umbrella", "handbag", "tie", "bottle", "cup", "fork", "knife", "spoon",
              "bowl", "chair", "sofa", "plant", "bed", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
              "cell phone", "book", "clock", "torch"
              ]

def process_image(img_str):
    # convert base64 string to numpy array
    img_bytes = base64.b64decode(img_str)
    np_img = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # perform object detection
    results = model(img)

    # process results...
    return results



# if __name__ == '__main__':
#     app.run(debug=True)
