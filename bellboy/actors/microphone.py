# Using uberi speech_recognition
# pip install SpeechRecognition
# requires pyaudio. on windows I had to "pipwin install pyaudio" bc pyaudio not compatible w python3.7

# pocket sphinx for local speech recognition
# need to download swig for c/c++ support (?). add swig to ur Path 
# python -m pip install --upgrade pip setuptools wheel
# pip install --upgrade pocketsphinx

# google cloud for cloud pip install google-cloud-speech
#

import speech_recognition as sr
import time
from threading import Thread
# from actors.generic import GenericActor

# class MicrophoneActor(GenericActor):
#     """
#     Class for the voice recognition microphone.
#     """

#     def __init__(self):
#         super().__init__()

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

# # recognize speech using Sphinx
# try:
#     print("Sphinx thinks you said " + r.recognize_sphinx(audio))
# except sr.UnknownValueError:
#     print("Sphinx could not understand audio")
# except sr.RequestError as e:
#     print("Sphinx error; {0}".format(e))


# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))



    
