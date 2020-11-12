
import cv2
import numpy as np
from PIL import Image
import os

<<<<<<< HEAD
def collectNewFace():
    count = 0
    face_id = input('\n enter user id and press <return> ==>  ')
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    while(True):
        ret, img = cam.read()
        img = cv2.flip(img, 1)  # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            count += 1
            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h, x:x+w])
            #cv2.imshow('image', img)
        k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30:  # Take 30 face sample and stop video
            break
    print('Done Collecting')
    trainDataSet()


def trainDataSet():
    faces, ids = getImagesAndLabels('dataset')
    print('Done Getting Images')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    recognizer.write('trainer/trainer.yml')  # recognizer.save() worked on Mac, but not on Pi
    print('Done Training')
# function to get the images and label data


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
   
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
        img_numpy = np.array(PIL_img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)
    return faceSamples, ids

# function to run at all times


def recognizeFace():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('./trainer/trainer.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # iniciate id counter
    id = 0
    floorNum = 0
    # names related to ids: example ==> Marcelo: id=1,  etc
    names = ['none', 'Marcelo', 'Peter', 'Dan', 'Yusra', 'Elma', 'Ryan', 'shriya', 'Nevin', 'Sein']
    floors = ['G', 2, 4, 6, 17, 18, 42, 63, 2, 9]
    # Initialize and start realtime video capture
    
    cam.set(3, 640)  # set video widht
    cam.set(4, 480)  # set video height
=======
def collectNewFace(cam, face_id):
    count = 0
    face_id = input('\n enter user id and press <return> ==>  ')
    while(True):
        ret, img = cam.read()
        img = cv2.flip(img,1) # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imshow('image', img)
        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30: # Take 30 face sample and stop video
             break
    trainDataSet()

def trainDataSet():
    faces,ids = getImagesAndLabels('dataset')
    recognizer.train(faces, np.array(ids))
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
    return faceSamples,ids

# function to run at all times
def recognizeFace():
    font = cv2.FONT_HERSHEY_SIMPLEX
    #iniciate id counter
    id = 0
    floorNum = 0
    # names related to ids: example ==> Marcelo: id=1,  etc
    names = ['none','Marcelo','Peter','Dan','Yusra','Elma','Ryan','shriya','Nevin','Sein'] 
    floors = ['G',2,4,6,17,18,42,63,2,9]
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(-1)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height
>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:
<<<<<<< HEAD
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
            print(id2)
            # Check if confidence is less them 100 ==> "0" is perfect match
=======
        ret, img =cam.read()
        img = cv2.flip(img, 1) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id2, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match 
>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
            if (confidence < 100):
                id = names[id2]
                floorNum = floors[id2]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
<<<<<<< HEAD
                collectNewFace()
                recognizer = cv2.face.LBPHFaceRecognizer_create()
=======
>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
                recognizer.read('trainer/trainer.yml')
                cascadePath = "haarcascade_frontalface_default.xml"
                faceCascade = cv2.CascadeClassifier(cascadePath)
                id = "unknown"
                floorNum = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
<<<<<<< HEAD

            cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
            cv2.putText(img, "Floor "+str(floorNum), (x+h, y-5), font, 1, (255, 255, 255), 2)
        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    cam = cv2.VideoCapture(-1)
    recognizeFace()
=======
            
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
            cv2.putText(img, "Floor "+str(floorNum), (x+h,y-5), font, 1, (255,255,255), 2)
        cv2.imshow('camera',img) 

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

if __name__ == "__main__" :
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    recognizeFace()
>>>>>>> 372584cf1e11cd5f7bf8e6e2476305cb78dcb8b5
