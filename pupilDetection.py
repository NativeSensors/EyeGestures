import cv2
import dlib
import time
import queue
import pickle
import random
import threading
import numpy as np
from typing import Callable, Tuple
from eyeGestures.eye import Eye
from eyeGestures.utils import VideoCapture

if __name__ == "__main__":    
    print("opening stream")
    # vid = VideoCapture('recording/calibrationData1.pkl')
    vid = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    
    print("loading detectors")
    facePredictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    faceDetector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # use half of the data for fitting
    pFrame = None
    flow = None
    ret = True
    print("starting reading")
    while ret:
        
        ret, frame = vid.read()
        
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        try:
            (x, y, w, h) = faceDetector.detectMultiScale(gray, 1.1, 9)[0]
            face = facePredictor(gray, dlib.rectangle(x, y, x+w, y+h))
            rect = face.rect
            lt_corner = (rect.left(),rect.top())
            rb_corner = (rect.right(),rect.bottom())

            landmarks = np.zeros((face.num_parts, 2), dtype=np.dtype)
            for i in range(0, face.num_parts):
                landmarks[i] = (face.part(i).x, face.part(i).y)

            eyeLeft  = Eye(gray,landmarks,0)
            eyeRight = Eye(gray,landmarks,1)

            cv2.circle(frame,eyeLeft.getPupil(),2,(0,0,255),1)
            for point in eyeLeft.getLandmarks():
                cv2.circle(frame,point,2,(0,255,0),1)

            cv2.circle(frame,eyeRight.getPupil(),2,(0,0,255),1)
            for point in eyeRight.getLandmarks():
                cv2.circle(frame,point,2,(0,255,0),1)

            cv2.rectangle(frame,lt_corner,rb_corner,(0,0,255),1)
        except Exception as e:
            print(f"Caught exception: {e}")
            pass

        cv2.imshow("frame",frame)
        if cv2.waitKey(10) == ord('q'):
            run = False
            break         

    cv2.destroyAllWindows()