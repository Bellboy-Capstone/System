import os
import pickle
# import time
from threading import Thread

import cv2
# import face_recognition this import up here causes ActorSystem to fail! i think bc AS has a time out and this import takes too long
from actors.generic import GenericActor
# from collections import deque
# # from picamera import PiCamera
from utils.messages import CameraType, CamEventMsg, CamMsg, CamReq, CamResp, Response


face_data_dir = "utils/facial/dataset"
NUM_TRAINING_PICS = 3 # how many pics we want to take to train a new face

# # create the cascade classifier (not needed if face detection done thru FR package)
cascPath = cascadePath = (
    os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_default.xml"
)
faceCascade = cv2.CascadeClassifier(cascPath)


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

        self.pics_to_take  = 0
        self.known_encodings = []
        self.encodings_to_id = {}
        self.unknown_encodings = []  # where pics tentavive to store are held
        self.unknown_size = 0
        self.MODEL = None  # face detection model, hog (default) or cnn (slower, more accurate & gpu accelerated)
        self.TOLERANCE = 0
        self.next_id = 0


    # STATE METHODS
    def setup_camera(self, camera_type, model="hog", tolerance=0.8):
        """ Sets up camera.
        """
        self.cameraType = camera_type 

        if self.cameraType == CameraType.RPI_CAM:
            self.camera = PiCamera()
            self.loop_method = self.rpi_streaming_loop

        elif self.cameraType == CameraType.USB_CAM:
            self.camera = cv2.VideoCapture(0)
            self.loop_method = self.usb_streaming_loop

        self.MODEL = model  # face detection model, hog (default) or cnn (slower, more accurate & gpu accelerated)
        self.TOLERANCE = tolerance
        self.load_faces()
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
        """ Camera streaming loop for rpi cameras """        
        pass

    def usb_streaming_loop(self):
        """
        Streaming thread for USB cameras.
        The thread:
            - Looks for face
            - if face is found:
                - if face doesnt exist, recognize them to our database
                - send presence event 
        """
        
        import face_recognition # lol
        self.status = CamResp.STREAMING
        self.log.info("Start streaming loop...")
        process_this_frame = False
        
        while self.threadOn:
            # Capture frame-by-frame
            ret, frame = self.camera.read()
            if ret == False:  # no frames were grabbed
                # print("no frames")
                continue

            # process every other frame
            process_this_frame = not process_this_frame
            if process_this_frame is False:
                continue

            # Resize frame of video to 1/4 size for faster face recognition processing
            # mini_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # grayscale the image, and change bgr -> rgb
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # find the faces in the image as a list of their bbox coordinates
            # TODO can change to FR face detection cus opencv's is sus
            rects = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            # reorder the coordinates for FR
            face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # hash the faces in the frame into their encodings
            face_encodings = face_recognition.face_encodings(rgb, face_locations)

            if self.pics_to_take > 0:
                # TRAINING SEQUENCE
                # just save the pics if we are in training mode
                if len(face_encodings) >= 1:
                    
                    self.encodings_to_id[len(self.known_encodings)] = self.next_id
                    self.known_encodings.append(face_encodings[0])
                    self.pics_to_take -= 1

                    # print( "Saved pic %d of new face"%(NUM_TRAINING_PICS - self.pics_to_take) )

                if self.pics_to_take == 0:
                    # assign this unknown person to our next id
                    # TODO ensure the pics are indeed of the same person
                    self.log.debug("Assigned ID of %d to new face" %self.next_id)
                    self.next_id += 1

            else:
                # IDENTIFICATION SEQUENCE
                # compare the encoding against the known encodings
                for encoding in face_encodings:

                    matches = face_recognition.compare_faces(
                        self.known_encodings, encoding, tolerance=self.TOLERANCE
                    )

                    # find first match
                    ix = -1
                    faceIx = -1  # index of unknown face
                    for result in matches:
                        ix += 1
                        if result == True:
                            faceIx = ix
                            break

                    if faceIx == -1:
                        print("New person detected")
                        self.pics_to_take = NUM_TRAINING_PICS  # trigger training sequence on next run

                    else:
                        self.log.debug(
                            "Person found: %d" %self.encodings_to_id[faceIx],
                        )
                        # cv2.putText(frame, faceIx, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            # draw boxes around the faces
            for (y1, x2, y2, x1) in face_locations:

                # Draw a rectangle around the face, top left to bottom right corner
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # finally, display the resulting frame
            cv2.imshow("Video", frame)
            
        self.log.info("Streaming terminated.")
        self.status = CamResp.SET


    def load_faces(self):
        """ loads the face encodings from file directory"""

        curr_size = 0
        for pickle_file in os.listdir(face_data_dir):
            # TODO ensure its a pickle file
            pickle_file = os.path.join(face_data_dir, pickle_file)
            faceId = int(pickle_file.split("_")[1])
            with open(pickle_file, "rb") as f:

                # dump their encodings onto our known
                encodings = pickle.load(f)
                self.known_encodings.extend(encodings)
                
                # map all their encodings to their id
                for i in range(curr_size, curr_size + len(encodings)):
                    self.encodings_to_id[i] = faceId
                    # print("associated the %d known encoding to person %d" %(i, faceId))

                self.next_id = faceId + 1
                curr_size += len(encodings)

    def save_encodings(self):
        self.log.debug("saving encodings to pickle file")
        prevId = -1
        currId = -1
        faceList = []
        ix = 0
        while ix < len(self.known_encodings):
            currId = self.encodings_to_id[ix]
            if prevId != currId:
                if faceList != []:
                    # save pickle file for prev batch
                    with open(os.path.join(face_data_dir, "faces_%d"%prevId), "wb") as f:
                        pickle.dump(faceList, f)
                    
                    faceList = []
            
            faceList.append(self.known_encodings[ix])
            prevId = currId
            ix += 1
    
        # save pickle file for last batch
        if faceList != []:
            with open(os.path.join(face_data_dir, "faces_%d"%prevId), "wb") as f:
                pickle.dump(faceList, f)

    def clear(self):
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
            self.setup_camera(msg.CamNumber)

            if self.status != CamResp.SET:
                self.send(sender, Response.FAIL)
            else:
                self.send(sender, self.status)


    def receiveMsg_CamReq(self, msg, sender):
        self.log.info("Received message %s from %s", msg.name, self.nameOf(sender))

        if msg == CamReq.SETUP:
            self.setup_camera(CameraType.USB_CAM)

        if msg == CamReq.START_STREAM:
            self.start_streaming()

        if msg == CamReq.STOP_STREAM:
            self.stop_streaming()


    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown. (i.e. close threads, disconnect from services, etc)
        """
        self.stop_streaming()
        self.save_encodings()
        self.clear()

    def summary(self):
        """
        Returns a summary of the actor. The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        return self.cameraType