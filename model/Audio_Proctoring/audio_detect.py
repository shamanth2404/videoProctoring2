import os
import threading
import wave
import time
import pyaudio
import numpy as np
import librosa
import speech_recognition as sr
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize


# Ensure you have NLTK data downloaded
# nltk.download('stopwords')
# nltk.download('punkt')

# Parameters
SAMPLE_RATE = 44100
DURATION = 10  # Number of seconds to record at once
N_MELS = 128

# Heuristic thresholds for noise vs speech
VOLUME_THRESHOLD = 0.003
SPEECH_FREQUENCY_THRESHOLD = 300  # Example frequency threshold

def read_audio(stream, filename):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    frames = []  # Initialize array to store frames
    
    for _ in range(0, int(SAMPLE_RATE / chunk * DURATION)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    # Stop and close the stream
    stream.stop_stream()
    stream.close()

def convert(i):
    if i >= 0:
        sound = 'record' + str(i) + '.wav'
        r = sr.Recognizer()
        
        with sr.AudioFile(sound) as source:
            r.adjust_for_ambient_noise(source)
            print("Converting Audio To Text and saving to file.....") 
            audio = r.listen(source)
        try:
            value = r.recognize_google(audio)
            os.remove(sound)
            result = "{}".format(value)
 
            with open("test.txt", "a") as f:
                f.write(result)
                f.write(" ")
                
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except KeyboardInterrupt:
            pass

p = pyaudio.PyAudio()  # Create an interface to PortAudio
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2

def save_audios(i):
    stream = p.open(format=sample_format, channels=channels, rate=SAMPLE_RATE,
                    frames_per_buffer=chunk, input=True)
    filename = 'record' + str(i) + '.wav'
    read_audio(stream, filename)

    # Load the audio file and analyze
    audio, sr = librosa.load(filename, sr=SAMPLE_RATE, duration=DURATION)
    volume = np.mean(librosa.feature.rms(y=audio))
    centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))

    #print(f"Recorded Audio {i}: Volume = {volume}, Spectral Centroid = {centroid}")
    if volume > VOLUME_THRESHOLD and centroid > SPEECH_FREQUENCY_THRESHOLD:
        print("Warning: Audio detected!")
    
for i in range(30 // DURATION):
    t1 = threading.Thread(target=save_audios, args=[i]) 
    x = i - 1
    t2 = threading.Thread(target=convert, args=[x])  # send one earlier than being recorded
    t1.start() 
    t2.start() 
    t1.join() 
    t2.join() 
    if i == 2:
        flag = True
if flag:
    convert(i)
    p.terminate()

# Process the transcribed text
with open("test.txt") as file:
    data = file.read()

stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(data)
filtered_sentence = [w for w in word_tokens if not w in stop_words]

with open('final.txt', 'w') as f:
    for ele in filtered_sentence:
        f.write(ele + ' ')

# Check if proctor needs to be alerted
with open("paper.txt") as file:  # Question file
    data = file.read()

word_tokens = word_tokenize(data)
filtered_questions = [w for w in word_tokens if not w in stop_words]

def common_member(a, b):     
    a_set = set(a) 
    b_set = set(b) 
    return a_set.intersection(b_set)

common_elements = common_member(filtered_sentence, filtered_questions)
if common_elements:
    print(common_elements)
    print("Alert: Student may be referring to exam questions.")

