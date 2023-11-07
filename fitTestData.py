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
from utils.utils import detectFace, getEyes, getCoordinates, var, VideoCapture

if __name__ == "__main__":
    run = True
    display = CalibrationDisplay()
    etracker = EyeTracker()
    
    frames = []
    with open('recording/calibrationData1.pkl', 'rb') as file:
        frames = pickle.load(file)
    #print("After URL")

    fPoints = []
    calPoitns = []
    
    division = 480
    training = frames[:division]
    test     = frames[division:]
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
        
    # fPoints = fPoints[:-1]
    print(f"calPoitns: {np.array(calPoitns).shape}, fPoints: {np.array(fPoints).shape}")
    etracker.fit(np.array(calPoitns), np.array(fPoints))

    # Get the current time
    for cPoint, frame in training:
        cv2.imshow("frame",frame)

        display.clean()
        detectFace(frame, 
            lambda faceSquare, landmarks, bounding_box   : getEyes(frame, faceSquare, landmarks, bounding_box,
                lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                    lambda left_coors, right_coors       : (print(f"point: {np.array((left_coors,right_coors))}"),display.drawPoint(etracker.predict(np.array((left_coors,right_coors))),(255,0,0),"estimatedPoint"))
                    )
                )
            )
        display.drawPoint(cPoint,(0,0,255),"callibrationPoint")
        display.show()

        if cv2.waitKey(1000) == ord('q'):
            run = False
            break                        

            #show point on sandbox
    cv2.destroyAllWindows()