''''
Real Time Face Recogition
	==> Each face stored on dataset/ dir, should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model (trained faces) should be on trainer/ dir
Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18  

'''

#from faceFucns import collectNewFace
import os
import cv2
import numpy as np
<<<<<<< HEAD
=======
import os 
import faceFucns 


>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

font = cv2.FONT_HERSHEY_SIMPLEX

# iniciate id counter
id = 0
floorNum = 0

# names related to ids: example ==> Marcelo: id=1,  etc

names = ['none', 'Marcelo', 'Peter', 'Dan', 'Yusra', 'Elma', 'Ryan', 'shriya', 'Nevin', 'Sein']
floors = ['G', 2, 4, 6, 17, 18, 42, 63, 2, 9]

<<<<<<< HEAD
=======
names = ['none', 'Marcelo', 'Peter', 'Dan', 'Yusra', 'Elma', 'Ryan', 'shriya', 'Nevin', 'Sein']
floors = ['G', 2, 4, 6, 17, 18, 42, 63, 2, 9]

>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
# Initialize and start realtime video capture

cam = cv2.VideoCapture(-1)
cam.set(3, 640)  # set video widht
cam.set(4, 480)  # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

while True:

    ret, img = cam.read()
    img = cv2.flip(img, 1)  # Flip vertically

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

    for(x, y, w, h) in faces:

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        id2, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            id = names[id2]
            floorNum = floors[id2]
            confidence = "  {0}%".format(round(100 - confidence))
        else:

            id = "unknown"
            floorNum = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))

        cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
        cv2.putText(img, "Floor "+str(floorNum), (x+h, y-5), font, 1, (255, 255, 255), 2)
    cv2.imshow('camera', img)

    k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()