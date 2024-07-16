import base64
import matplotlib.pyplot as plt
from flask import Flask
from flask_cors import CORS
import os
from flask import request, jsonify
import tensorflow as tf 
import tensorflow_hub as hub 
import cv2 
import numpy as np
from test_eye import process_image
from test_headpose import process_image as process_head_image
from Audio_Proctoring.test_audio_detect import start_recording,process_text
from mouth_tracking import mouth_track
from background_apps import detect_windows
from vps_motionDetectionModuleMain.hand_gesture.test_hand import hand_track
from with_liveness_face_detection.test_headposing import process_image as process_headpose_image
from vps_motionDetectionModuleMain.phoneAndPerson.phoneAndPerson2.test_phoneUsage import YoloV3, load_darknet_weights
import secrets
import asyncio
from bleak import BleakScanner
import win32com.client

app = Flask(__name__)
CORS(app)

app.secret_key = secrets.token_hex(16)
yolo = YoloV3()
current_dir = os.path.dirname(__file__)
os.path.join(current_dir, 'vps_motionDetectionModuleMain\\phoneAndPerson\\phoneAndPerson2\\yolov3weights.weights')
load_darknet_weights(yolo, os.path.join(current_dir, 'vps_motionDetectionModuleMain\\phoneAndPerson\\phoneAndPerson2\\yolov3weights.weights'))

# Define the class names
class_names = [c.strip() for c in open(os.path.join(current_dir, 'vps_motionDetectionModuleMain\\phoneAndPerson\\phoneAndPerson2\\Classes.TXT')).readlines()]

def readb64(uri):
    try:
        encoded_data = uri.split(',')[1]
        nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

@app.route('/eye_tracking', methods=['POST'])
def eye_tracking():
    try:
        data = request.get_json(force=True)
        image_b64 = data['img']
        email = data['email']
        image = readb64(image_b64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        result = process_image(image,email)
        return jsonify(result)
    except Exception as e:
        print(f"Error in /eye_tracking: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/head_tracking', methods=['POST'])
def head_tracking():
    try:
        data = request.get_json(force=True)
        image_b64 = data['img']
        image = readb64(image_b64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        result = process_head_image(image)
        return jsonify(result)
    except Exception as e:
        print(f"Error in /head_tracking: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/headposing_tracking', methods=['POST'])
def headposing_tracking():
    try:
        data = request.get_json(force=True)
        image_b64 = data['img']
        email = data['email']
        image = readb64(image_b64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        result = process_headpose_image(image,email)
        return jsonify(result)
    except Exception as e:
        print(f"Error in /head_tracking: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = os.path.join("uploads", file.filename)
        file.save(filename)
        response = process_uploaded_audio(filename)
        return jsonify(response)

@app.route('/phone_tracking', methods=['POST'])
def phone_tracking():
    # if 'img' not in request.files:
    #     return jsonify({'error': 'No image provided'}), 400

    data = request.get_json(force=True)
    image_b64 = data['img']
    image = readb64(image_b64)
    if image is None:
        return jsonify({'error': 'Failed to decode image'}), 400
    
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (320, 320))
    img = img.astype(np.float32)
    img = np.expand_dims(img, 0)
    img = img / 255.0

    boxes, scores, classes, nums = yolo(img)
    detections = []
    # for i in range(nums[0]):
    #     if int(classes[0][i] == 0):
    #         count +=1
    #     if int(classes[0][i] == 67):
    #         print('Mobile Phone detected')
    #     if int(classes[0][i] == 65):
    #        print('Remote Detected')
    # if count == 0:
    #     print('No person detected')
    # elif count > 1:
    #     print('More than one person detected')
    for i in range(nums[0]):
        detections.append({
            'class': class_names[int(classes[0][i])],
            'score': float(scores[0][i]),
            'box': boxes[0][i].numpy().tolist()
        })

    person_count = sum(1 for detection in detections if detection['class'] == 'person')

    other_classes_present = any(detection['class'] != 'person' for detection in detections)

    if person_count >= 2:
        return jsonify({"warning": "Multiple people detected"})
    elif other_classes_present:
        return jsonify({"warning": "Electronic Gadgets detected"})

    return jsonify(detections)

@app.route('/start-recording', methods=['POST'])
def audio_start():
    result = start_recording()
    return (result)

@app.route('/process-text', methods=['POST'])
def process_audio_text():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid input'}), 400

    # Extract testCode from the JSON data
    testCode = data.get('testCode')
    print(testCode)
    if not testCode:
        return jsonify({'error': 'testCode is required'}), 400
    result = process_text(testCode)
    return (result)

@app.route('/mouth_tracking', methods=['POST'])
def mouth_tracking():
    # Get the image file from the request
        data = request.get_json(force=True)
        image_b64 = data['img']
        email = data['email']
        img = readb64(image_b64)
        
        res = mouth_track(img,email)
        
        # Return a response (for example, a JSON response)
        return (res)
    
@app.route('/hand_tracking', methods=['POST'])
def hand_tracking():
    # Get the image file from the request
        data = request.get_json(force=True)
        image_b64 = data['img']
        img = readb64(image_b64)
        
        res = hand_track(img)
        
        # Return a response (for example, a JSON response)
        return (res)
    
@app.route('/window_tracking', methods=['GET'])
def window_tracking():        
        res = detect_windows()
        
        # Return a response (for example, a JSON response)
        return (res)


@app.route('/bluetooth/status', methods=['GET'])
def bluetooth_status():
    async def is_bluetooth_on():
        try:
            devices = await BleakScanner.discover(timeout=5)
            if devices:
                return True
            else:
                return False
        except Exception as e:
            print(f"Bluetooth error: {e}")
            return False

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bluetooth_on = loop.run_until_complete(is_bluetooth_on())
    return jsonify({'bluetooth_on': bluetooth_on})

# Route to list connected USB devices
@app.route('/usb/devices', methods=['GET'])
def usb_devices():
    def list_usb_devices():
        wmi = win32com.client.GetObject("winmgmts:")
        usb_devices = wmi.ExecQuery("Select * from Win32_USBHub")
        known_internal_devices = ["USB Root Hub", "USB Composite Device"]
        external_devices = [device.Description for device in usb_devices if not any(internal in device.Description for internal in known_internal_devices)]
        return external_devices

    devices = list_usb_devices()
    return jsonify({'usb_devices': devices})
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=8080)