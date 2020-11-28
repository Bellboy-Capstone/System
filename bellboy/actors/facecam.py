import time
from threading import Thread

from actors.generic import GenericActor
from collections import deque
from picamera import PiCamera
from utils.camera.facial.FacialRecognition.faceFuncs import recognizeFace
from utils.camera.rpi_camera_surveillance_system import StreamingOutput
from utils.messages import CameraType, CamMsg, CamReq, CamResp, Response, CamEventMsg


class FacecamActor(GenericActor):
    """
    Class for the facial camera.
    """
    def __init__(self):
        super().__init__()
        self.camera = None
        self.cameraType = None
        self.recording_thread = None
        self.loop_method = None
        self.threadOn = False


    # STATE METHODS
    def setupCamera(self, camera_type):
        """ Sets up camera.
        """
        self.cameraType = camera_type 

        if self.cameraType == CameraType.RPI_CAM:
            self.camera = PiCamera()
            self.loop_method = self.rpi_streaming_loop

        elif self.cameraType == CameraType.USB_CAM:
            self.camera = cv2.VideoCapture(-1)
            self.loop_method = self.usb_streaming_loop

        self.status = CamResp.SET

    def start_streaming(self):

        """Triggers streaming thread to begin.
        """        
        if self.status != CamResp.SET:
            self.log.warning("Cam not setup!")
            return

        if self.status == CamResp.STREAMING:
            self.log.info("Alreay streaming!")
            return

        self.threadOn = True
        self.recording_thread = Thread(target=self.loop_method)            
        self.recording_thread.start()

    def stop_streaming(self):
        if not self.threadOn:
            self.log.info("Not streaming")
            return

        self.log.debug("Terminating streaming thread ...")
        self.threadOn = False

    def rpi_streaming_loop(self):
        """ Camera streaming loop for rpi cameras
        """        
        self.status = CamResp.STREAMING
        self.log.info("Start streaming loop...")

        while self.threadOn:
            self.log.debug("inside loop ..")
            time.sleep(5)

            #             #show hand cam
            # with picamera.PiCamera(resolution='640x480', framerate=60) as camera:
            # output = StreamingOutput()
            # #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            # #camera.rotation = 90
            # camera.start_recording(output, format='mjpeg')
            # try:
            #     address = ('', 8000)
            #     server = StreamingServer(address, StreamingHandler)
            #     server.serve_forever()
            # finally:
            #     camera.stop_recording()
                           
        
        self.log.info("Loop terminated.")
        self.status = CamResp.SET

    def usb_streaming_loop(self):
        """
        Streaming thread for USB cameras.
        The thread:
            - Looks for face
            - if face is found:
                - if face doesnt exist, recognize them to our database
                - send presence event 
        """

        self.status = CamResp.STREAMING
        self.log.info("Start streaming loop...")
        
        while self.threadOn:
            
            # pseudo code
            # look for a face, with timeout of course
            try:
                face = wait_for_face(timeout = 60)
                if face not in saved_faces:
                    associate(saved_faces.nextId, face) # save face and associate it to the next available id
                event_msg = CamEventMsg(eventType = CamEvent.FACE_DETECTED, face = face, faceId = getFaceId(face))
                self.send(self.parent, event_msg)

            except TimeoutError:
                self.log.debug("No one detected.")
            
        self.log.info("Streaming terminated.")
        self.status = CamResp.SET


    def clear(self, camNumber):
        """
        Clears camera, returning actor to READY state.
        """ 
        if self.cameraType == CameraType.RPI_CAM:
            self.clear_rpi_cam()
        
        if self.cameraType == CameraType.USB_CAM:
            self.clear_usb_cam()
        
        self.status = Response.READY

    def clear_rpi_cam(self):
        # self.camera.stop_recording()
        # self.log.debug("Shutdown Handcam")     
        pass

    def clear_usb_cam(self):
        # self.camera.release()
        # self.cv2.destroyAllWindows()
        # self.log.debug("Shutdown Facecam")
        pass

    # MESSAGE HANDLING
    def receiveMsg_CamMsg(self, msg, sender):
        self.log.info("Received message %s from %s", msg, self.nameOf(sender))
        
        if msg.msgType == CamReq.SETUP:
            self.setupCam(msg.CamNumber)

            if self.status != CamResp.SET:
                self.send(sender, Response.FAIL)
            else:
                self.send(sender, self.status)




    def receiveMsg_CamReq(self, msg, sender):
        self.log.info("Received message %s from %s", msg.name, self.nameOf(sender))

        if msg == CamReq.START_STREAMING:
            self.start_streaming()

        if msg == CamReq.STOP_STREAMING:
            self.stop_streaming()


    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown. (i.e. close threads, disconnect from services, etc)
        """
        self.stop_streaming()
        self.clear()

    def summary(self):
        """
        Returns a summary of the actor. The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        pass
