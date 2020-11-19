import time
from threading import Thread

import gpiozero
from picamera import PiCamera
from gpiozero.pins.mock import MockFactory
from actors.generic import GenericActor
from collections import deque
#from utils.messages import
from bellboy.actors.generic import GenericActor

# from bellboy.utils.messages import

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


pass