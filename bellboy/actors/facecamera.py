import os
import pickle

import cv2
import face_recognition


# pip install numpy==1.18
# to resolve the multiarray error :/

faces_pickle_file = "face_encodings.pkl"
saved_faces = []
known_encodings = []
temp_unknown_pics = []  # where pics tentavive to store are held
temp_pics_size = 0
MODEL = "hog"  # face detection model, hog (default) or cnn (slower, more accurate & gpu accelerated)
TOLERANCE = 0.6


class FaceCamera:
    """ Class for a facial camera"""

    def __init__(self):
        pass

    def load_faces(self):
        """ loads the faces from file """
        pass

    def demo(self):

        try:
            with open(faces_pickle_file, "rb") as f:
                known_encodings = pickle.load(f)
        except FileNotFoundError:
            known_encodings = []
            print("no pickle file exists :o")

        cascPath = cascadePath = (
            os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_default.xml"
        )
        faceCascade = cv2.CascadeClassifier(cascPath)
        try:
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

                # # grayscale the image
                # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # # find the faces in the image as a list of their bbox coordinates
                # face_locations = faceCascade.detectMultiScale(
                #     gray,
                #     scaleFactor=1.1,
                #     minNeighbors=5,
                #     minSize=(30, 30),
                #     flags=cv2.CASCADE_SCALE_IMAGE
                # )

                # Resize frame of video to 1/4 size for faster face recognition processing
                mini_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # fix image colour (?) BGR -> RGB

                # find the faces in the image as a list of their bbox coordinates
                face_locations = face_recognition.face_locations(
                    mini_frame, model=MODEL
                )  # slower, more consistent

                # hash the faces in the frame into their encodings
                curr_encodings = face_recognition.face_encodings(
                    mini_frame, face_locations
                )

                # compare the encoding against the known encodings
                for encoding in curr_encodings:
                    matches = face_recognition.compare_faces(
                        known_encodings, encoding, tolerance=TOLERANCE
                    )

                    # find first match
                    ix = -1
                    faceIx = -1  # index of unknown face
                    for result in matches:
                        ix += 1
                        if result == False:
                            continue

                        faceIx = ix
                        break

                    if faceIx == -1:
                        print(
                            "New person found, saving them to "
                            + str(len(known_encodings))
                        )
                        known_encodings.append(encoding)
                    else:
                        print("Person found: " + str(faceIx))
                #     #cv2.putText(frame, faceIx, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

                for (y1, x2, y2, x1) in face_locations:

                    # Draw a rectangle around the face, top left to bottom right corner
                    cv2.rectangle(
                        frame, (4 * x1, 4 * y1), (4 * x2, 4 * y2), (0, 0, 255), 2
                    )

                # Display the resulting frame
                cv2.imshow("Video", frame)

        except KeyboardInterrupt:
            pass
        finally:
            print("saving encodings to pickle file")
            with open(faces_pickle_file, "wb") as f:
                pickle.dump(known_encodings, f)

            # When everything is done, release the capture
            video_capture.release()
            cv2.destroyAllWindows()


facecam = FaceCamera()
facecam.demo()
