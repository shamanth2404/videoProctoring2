from flask import Flask, request, jsonify
import threading
import os
import wave
import pyaudio
import numpy as np
import librosa
import speech_recognition as sr
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from flask_cors import CORS
import os
import requests
from pymongo import MongoClient
# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Parameters
SAMPLE_RATE = 44100
DURATION = 10  # Number of seconds to record at once
N_MELS = 128

client = MongoClient('mongodb+srv://shamanthk2404:Shamanthk2404@cluster0.bgsebd6.mongodb.net/videoProctoring?retryWrites=true&w=majority&appName=Cluster0')  # Update the connection string if needed
db = client['videoProctoring']  # Replace with your database name
tests_collection = db['tests'] 

# Heuristic thresholds for noise vs speech
VOLUME_THRESHOLD = 0.003
SPEECH_FREQUENCY_THRESHOLD = 300  # Example frequency threshold

p = pyaudio.PyAudio()  # Create an interface to PortAudio
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2

def read_audio(stream, filename):
    frames = []
    for _ in range(0, int(SAMPLE_RATE / chunk * DURATION)):
        data = stream.read(chunk)
        frames.append(data)
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    stream.stop_stream()
    stream.close()

def convert(i):
    if i >= 0:
        sound = 'record' + str(i) + '.wav'
        r = sr.Recognizer()
        with sr.AudioFile(sound) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            value = r.recognize_google(audio)
            os.remove(sound)
            result = "{}".format(value)
            print(result)
            current_dir = os.path.dirname(__file__)

# Construct the relative path to the model
            relative_model_path = os.path.join(current_dir, 'test.txt')

            with open(relative_model_path, "a") as f:
                f.write(result)
                f.write(" ")
        except sr.UnknownValueError: 
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def save_audios(i):
    stream = p.open(format=sample_format, channels=channels, rate=SAMPLE_RATE, frames_per_buffer=chunk, input=True)
    filename = 'record' + str(i) + '.wav'
    read_audio(stream, filename)
    audio, sr = librosa.load(filename, sr=SAMPLE_RATE, duration=DURATION)
    volume = np.mean(librosa.feature.rms(y=audio))
    centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    if volume > VOLUME_THRESHOLD and centroid > SPEECH_FREQUENCY_THRESHOLD:
        print("Warning: Audio detected!")


def start_recording():
    global flag
    flag = False
    for i in range(30 // DURATION):
        t1 = threading.Thread(target=save_audios, args=[i])
        x = i - 1
        t2 = threading.Thread(target=convert, args=[x])
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        if i == 2:
            flag = True
    if flag:
        convert(i)        

    return jsonify({"status": "recording finished"})


def process_text(test_code):
    print("Process Text Running")
    current_dir = os.path.dirname(__file__)

# Construct the relative path to the model
    relative_model_path = os.path.join(current_dir,  'test.txt')

    with open(relative_model_path) as file:
        data = file.read()
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(data)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    relative_model_path = os.path.join(current_dir, 'final.txt')
    with open(relative_model_path, 'w') as f:
        for ele in filtered_sentence:
            f.write(ele + ' ')
    # with open("C:\\Users\\shamu\\OneDrive\\Desktop\\aankh\\model\\Audio_Proctoring\\paper.txt") as file:
    #     data = file.read()   
    test_doc = tests_collection.find_one({"test_code": test_code})
    if not test_doc:
        return jsonify({"error": "Test not found"}), 404
    
    keywords = test_doc.get('keywords', [])
    print(keywords)
    
        
    # word_tokens = word_tokenize(data)    
    # print(word_tokens)
    # filtered_questions = [w for w in word_tokens if not w in stop_words]
    def common_member(a, b):
        a_set = set(a)
        b_set = set(b)
        return a_set.intersection(b_set)
    common_elements = common_member(filtered_sentence, keywords)
    print(common_elements,filtered_sentence)    

    open(os.path.join(current_dir, 'test.txt'),'w').close()
    open(os.path.join(current_dir, 'final.txt'), 'w').close()

    if common_elements:
        return jsonify({"alert": "Student may be referring to exam questions.", "common_elements": list(common_elements)})
    return jsonify({"status": "No cheating detected."})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=8000)
