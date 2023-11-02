import cv2
import dlib
import pickle
import numpy as np
from typing import Callable, Tuple
from utils.eyeframes import eyeFrame, faceTracker
from utils.eyetracker import EyeSink

LEFT  = 0
RIGHT = 1

predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
tracker = faceTracker()
sandbox = np.zeros([512,512,3],dtype=np.uint8)
sandbox.fill(255)

def detectFace(gray : np.ndarray, onFace : Callable[[np.ndarray, np.ndarray, np.ndarray, (int,int,int,int)], None]):
    # hog_face_detector = dlib.get_frontal_face_detector()

    for (x, y, w, h) in face_cascade.detectMultiScale(gray, 1.1, 9):
        
        landmarks  = shape_to_np(predictor(gray, dlib.rectangle(x, y, x+w, y+h)))
        faceSquare = gray[x:x+w,y:y+h]
        
        onFace(faceSquare ,landmarks, (x, y, w, h))

def getCoordinates(left_eye_region : np.ndarray, right_eye_region : np.ndarray, onCoordinates : Callable[[(int,int),(int,int)], None]): 

    sink = EyeSink()

    left = sink.push(left_eye_region)
    right = sink.push(right_eye_region)

    left_eye_show = left_eye_region
    right_eye_show = right_eye_region

    onCoordinates(left,right)
    # (lcX,lcY) = left
    # (rcX,rcY) = right
    # (h,w,c) = left_eye_show.shape
    # cv2.circle(left_eye_show,(int(rcX*w),int(rcY*h)),2,(255,0,0),1)
    # (h,w,c) = right_eye_show.shape
    # cv2.circle(right_eye_show,(int(lcX*w),int(lcY*h)),2,(0,0,255),1)
    # cv2.imshow("left_eye_region", left_eye_show)
    # cv2.imshow("right_eye_region",right_eye_show)


def getEyes(image : np.ndarray,
            faceSquare : np.ndarray,
            landmarks : np.ndarray,
            coordinates : (int,int,int,int),
            onEyes : Callable[[np.ndarray,np.ndarray], None]):

    eFrame = eyeFrame()
    (x, y, w, h) = coordinates
    eFrame.setParams(image,faceSquare, landmarks, (x, y, w, h))
    tracker.update(eFrame)      
    
    left_eye_region  = eFrame.getLeftEye()
    right_eye_region = eFrame.getRightEye()
    
    onEyes(left_eye_region,right_eye_region)

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords


def showCoordinates(left,right):
    sandbox.fill(255)
    (lcX,lcY) = left
    (rcX,rcY) = right

    cv2.circle(sandbox,(int(rcX*512),int(rcY*512)),2,(255,0,0),1)
    cv2.circle(sandbox,(int(lcX*512),int(lcY*512)),2,(0,0,255),1)
    cv2.imshow("sandbox",sandbox)
    
if __name__ == "__main__":
    frames = []
    run = True

    with open('recording/data31-10-2023-17:53:21.pkl', 'rb') as file:
        frames = pickle.load(file)

    while run:
        for n, frame in enumerate(frames):
            w = frame.shape[1]
            h = frame.shape[0]

            scale_percent = 60 # percent of original size
            width = int(w * scale_percent / 100)
            height = int(h * scale_percent / 100)
            dim = (width, height)
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

            detectFace(frame, 
                lambda faceSquare ,landmarks, bounding_box : getEyes(frame, faceSquare, landmarks, bounding_box,
                    lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                        lambda left_coors, right_coors : showCoordinates(left_coors, right_coors)
                        )
                    )
                )

            if cv2.waitKey(1) == ord('q'):
                run = False
                break                        

            #show point on sandbox
            
    cv2.destroyAllWindows()