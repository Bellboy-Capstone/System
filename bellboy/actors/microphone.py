import speech_recognition as sr
import time
from threading import Thread

from actors.generic import GenericActor
from utils.messages import MicEvent, MicMsg, MicEventMsg, MicReq, MicResp, Response

class MicrophoneActor(GenericActor):
    """
    Class for the voice recognition microphone. nnn
    """

    def __init__(self):
        super().__init__()
        self.microphone = None
        self.listening_thread = None
        self.threadOn = False
        self.recognizer = sr.Recognizer()

    def microphoneList(self):
        """return list of microphones in the system"""
        return self.sr.Microphone.list_microphone_names()

    # STATE METHODS
    def setupMicrophone(self, micNumber):
        """Choose system microphone to use as mic

        :param micNumber: microphone number as indexed by microphoneList()
        :type micNumber: int
        """
        self.micIx = micNumber
        self.status = MicResp.SET

    def listening_loop(self):
        """To run in mic's thread. Listens for speech."""

        self.status = MicResp.LISTENING
        timeout_sec = 30.0
        self.log.info("begun listening.")
        while self.threadOn:

            # do the processing
            with sr.Microphone(device_index=self.micIx) as source:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout_sec)
                    try:
                        recognized_audio = self.recognizer.recognize_google(audio)
                        self.log.info(
                            str.format("Someone said <<{}>>", recognized_audio)
                        )
                        if "floor" in str(recognized_audio):
                            self.send(
                                self.parent,
                                MicEventMsg(
                                    eventType=MicEvent.SPEECH_HEARD,
                                    speechHeard=str(recognized_audio),
                                ),
                            )
                    except sr.UnknownValueError:
                        self.log.debug("Google API: unknown speech heard")
                    
                    except speech_recognition.RequestError:
                        pass 
                        # use sphinx instead


                except sr.WaitTimeoutError:
                    self.log.debug(
                        str.format("Nothing was heard for {} seconds", timeout_sec)
                    )

        self.log.info("Stopped listening thread")
        self.status = MicResp.SET

    def start_listening(self):
        if self.status != MicResp.SET:
            self.log.warning("Mic not setup!")
            return

        if self.status == MicResp.LISTENING:
            self.log.info("Alreay listening!")
            return

        self.threadOn = True
        self.listening_thread = Thread(target=self.listening_loop)
        self.listening_thread.start()

    def stop_listening(self):
        if not self.threadOn:
            self.log.info("Not listening")
            return

        self.log.debug("Terminating listener thread")
        self.threadOn = False
        # join?

    # MSG HANDLING
    def receiveMsg_MicMsg(self, msg, sender):
        self.log.info(
            str.format("Received message {} from {}", msg, self.nameOf(sender))
        )
        if msg.msgType == MicReq.SETUP:
            self.setupMicrophone(msg.micNumber)

            if self.status != MicResp.SET:
                self.send(sender, Response.FAIL)

            else:
                self.send(sender, self.status)

    def receiveMsg_MicReq(self, msg, sender):
        self.log.info(
            str.format("Received message {} from {}", msg.name, self.nameOf(sender))
        )
        if msg == MicReq.GET_MIC_LIST:
            self.send(
                sender, MicMsg(msgType=MicResp.MIC_LIST, micList=microphoneList())
            )
        elif msg == MicReq.START_LISTENING:
            self.start_listening()

        elif msg == MicReq.STOP_LISTENING:
            self.stop_listening()

    # overrides
    def summary(self):
        return self.status

    def teardown(self):
        stop_listening()
