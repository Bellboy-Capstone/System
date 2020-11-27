import time
from threading import Thread

from picamera import PiCamera
from actors.generic import GenericActor
from collections import deque
from utils.messages import CamReq, CamResp, CamMsg, Response
from bellboy.actors.generic import GenericActor
from utils.openCV.FacialRecognition.03_face_recognition import


camera = PiCamera()

class CameraActor(GenericActor):
    """
    Class for the cameras.
    """

    def __init__(self):
        super().__init__()
        self.camera = None
        self.recording_thread = None
        self.threadOn = False

    def cameraList(self):
        """return list of cameras in the system"""
        return self.Canmera.list_camera_names()


#setup sequence(usb or picam)

    # STATE METHODS
    def setupCamera(self, camNumber):
        """Choose system camera

        :param camNumber: camera number as indexed by cameraList() either picam or facecam
        :type camNumber: int
        """
        self.camIx = camNumber
        self.status = CamResp.SET
    

    def streaming_loop(self):
        """to run the camera's thread, looks for faces"""

        self.status = CamResp.START_STREAMING
        self.log.info("started streaming...")
        while self.threadOn:
            #run facial recognition code, dont know how to import tho
            pass
        pass



    def start_streaming(self):
        if self.status != CamResp.SET:
            self.log.warning("Cam not setup!")
            return

        if self.status == CamResp.STREAMING:
            self.log.info("Alreay streaming!")
            return

        self.threadOn = True
      #  self.recording_thread = Thread(target=self.streaming_loop)
        self.recording_thread.start()

    def stop_streaming(self):
        if not self.threadOn:
            self.log.info("Not streaming")
            return

        self.log.debug("Terminating listener thread")
        self.threadOn = False

    # MSG HANDLING
    def receiveMsg_CamMsg(self, msg, sender):
        self.log.info(
            str.format("Received message {} from {}", msg, self.nameOf(sender))
        )
        if msg.msgType == CamReq.SETUP:
            self.setupCamrophone(msg.CamNumber)

            if self.status != CamResp.SET:
                self.send(sender, Response.FAIL)

            else:
                self.send(sender, self.status)

    def receiveMsg_CamReq(self, msg, sender):
        self.log.info(
            str.format("Received message {} from {}", msg.name, self.nameOf(sender))
        )
        if msg == CamReq.GET_CAM_LIST:
            self.send(
                sender, CamMsg(msgType=CamResp.CAM_LIST, CamList=CamList())
            )
        elif msg == CamReq.START_STREAMING:
            self.start_streaming()

        elif msg == CamReq.STOP_STREAMING:
            self.stop_streaming()


    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown. (i.e. close threads, disconnect from services, etc)
        """
        self.clear()

    def summary(self):
        """
        Returns a summary of the actor. The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        pass