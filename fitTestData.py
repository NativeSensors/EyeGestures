import cv2
import dlib
import time
import queue
import pickle
import random
import threading
import numpy as np
from typing import Callable, Tuple
from utils.eyetracker import EyeSink, EyeTracker, CalibrationCollector, CalibrationDisplay
from utils.utils import detectFace, getEyes, getCoordinates

# Bufforless
class VideoCapture:

    def __init__(self,name):
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        self.t = threading.Thread(target=self.__reader).start()

    def __reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break 
            if not self.q.empty():
                try: 
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return (not self.q.empty(), self.q.get())

class var:

    def __init__(self,var):
        self.__var = var

    def set(self,var):
        self.__var = var

    def get(self):
        return self.__var

if __name__ == "__main__":
    run = True
    display = CalibrationDisplay()
    calibration = CalibrationCollector(display.width,display.height)
    etracker = EyeTracker()
    
    frames = []
    with open('recording/calibrationData.pkl', 'rb') as file:
        frames = pickle.load(file)
    #print("After URL")

    fPoints = []
    calPoitns = []
    
    training = frames[:int(len(frames)/2)]
    test     = frames[int(len(frames)/2):]
    # use half of the data for fitting
    for cPoint, frame in training:
        
        detectFace(frame, 
            lambda faceSquare, landmarks, bounding_box   : getEyes(frame, faceSquare, landmarks, bounding_box,
                lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                    lambda left_coors, right_coors       : fPoints.append(np.array((left_coors,right_coors)))
                    )
                )
            )

        calPoitns.append(cPoint)
        
    fPoints = fPoints[:-1]
    print(f"calPoitns: {np.array(calPoitns).shape}, fPoints: {np.array(fPoints).shape}")
    etracker.fit(np.array(calPoitns), np.array(fPoints))

    # Get the current time
    for cPoint, frame in test:
        cv2.imshow("frame",frame)

        display.clean()
        detectFace(frame, 
            lambda faceSquare, landmarks, bounding_box   : getEyes(frame, faceSquare, landmarks, bounding_box,
                lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                    lambda left_coors, right_coors       : display.drawPoint(etracker.predict(np.array((left_coors,right_coors))),(255,0,0))
                    )
                )
            )
        display.drawPoint(cPoint,(0,0,255))
        display.show()

        if cv2.waitKey(1) == ord('q'):
            run = False
            break                        

            #show point on sandbox
    cv2.destroyAllWindows()