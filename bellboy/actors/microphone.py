# Using uberi speech_recognition
# requires pyaudio. on windows I had to "pipwin install pyaudio" bc pyaudio not compatible w python3.7

# pocket sphinx for local speech recognition
# Make sure we have up-to-date versions of pip, setuptools and wheel
# python -m pip install --upgrade pip setuptools wheel
# pip install --upgrade pocketsphinx

# google cloud for cloud pip install google-cloud-speech
#

import time
from threading import Thread
from actors.generic import GenericActor

class MicrophoneActor(GenericActor):
    """
    Class for the voice recognition microphone.
    """

    def __init__(self):
        super().__init__()

    
