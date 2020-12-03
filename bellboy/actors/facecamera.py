import os
import pickle

import cv2
import face_recognition


# pip install numpy==1.18
# to resolve the multiarray error :/


faces_pickle_file = "data.pkl"
face_data_dir = "utils/facial/dataset"
NUM_TRAINING_PICS = 3 # how many pics we want to take to train a new face

# create the cascade classifier (not needed if face detection done thru FR package)
cascPath = cascadePath = (
    os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_default.xml"
)
faceCascade = cv2.CascadeClassifier(cascPath)

class FaceCamera:
    """ Class for a facial camera"""


    def __init__(self, model="hog", tolerance=0.8):
        self.pics_to_take  = 0
        self.known_encodings = []
        self.encodings_to_id = {}
        self.unknown_encodings = []  # where pics tentavive to store are held
        self.unknown_size = 0
        self.MODEL = model  # face detection model, hog (default) or cnn (slower, more accurate & gpu accelerated)
        self.TOLERANCE = tolerance
        self.next_id = 0

    def load_faces(self):
        """ loads the face encodings from file directory"""

        curr_size = 0
        for pickle_file in os.listdir(face_data_dir):
            # TODO ensure its a pickle file
            pickle_file = os.path.join(face_data_dir, pickle_file)
            faceId = int(pickle_file.split("_")[1])
            with open(pickle_file, "rb") as f:

                # dump teir encodings onto our known
                encodings = pickle.load(f)
                self.known_encodings.extend(encodings)
                
                # map all their encodings to their id
                for i in range(curr_size, curr_size + len(encodings)):
                    self.encodings_to_id[i] = faceId
                    print("associated the %d known encoding to person %d" %(i, faceId))

                self.next_id = faceId + 1
                curr_size += len(encodings)

    def demo(self):
        """
        Demo of realtime facial recognition.
        Looks for faces. Unknown faces get saved. Kinda slow.
        Ideas for improvement:
            - parallelism w GPU
            - seperate thread to do the encodings on new faces (?)
            - use a dict to store encoding -> faceId, so multiple encodings of the same person can be stored
            - periodically cleanup data by grouping encodings that r too similar
            - limit search to the single most centralized face instead of looking for all faces
            - use a diff face recog library (DeepFace, OpenCV...etc)
        """
        video_capture = cv2.VideoCapture(0)
        process_this_frame = False

        while True:

            # Capture frame-by-frame
            ret, frame = video_capture.read()
            if ret == False:  # no frames were grabbed
                print("no frames")
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

                    print(
                        "Saved pic %d of new face"
                        %(NUM_TRAINING_PICS - self.pics_to_take),
                    )

                if self.pics_to_take == 0:
                    # assign this unknown person to our next id
                    # TODO ensure the pics are indeed of the same person
                    print("Assigned ID of %d to new face" %self.next_id)
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
                        print(
                            "Person found: %d" %self.encodings_to_id[faceIx],
                        )
                        # cv2.putText(frame, faceIx, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            # draw boxes around the faces
            for (y1, x2, y2, x1) in face_locations:

                # Draw a rectangle around the face, top left to bottom right corner
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # finally, display the resulting frame
            cv2.imshow("Video", frame)


            k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
            if k == 27:
                break

        print("saving encodings to pickle file")
        prevId = -1
        currId = -1
        faceList = []
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
        # When everything is done, release the capture
        video_capture.release()
        cv2.destroyAllWindows()


facecam = FaceCamera()
facecam.load_faces()
facecam.demo()
