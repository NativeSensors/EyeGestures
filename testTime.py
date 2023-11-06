import cv2
import dlib
import time
import pickle
import random
import numpy as np

from typing import Callable, Tuple
from utils.eyetracker import EyeSink, EyeTracker, CalibrationCollector, CalibrationDisplay
from utils.utils import detectFace, getEyes, getCoordinates

if __name__ == "__main__":
    frames = []
    run = True
    display = CalibrationDisplay()
    calibration = CalibrationCollector(display.width,display.height)
    etracker = EyeTracker()
    
    with open('recording/data31-10-2023-17:53:21.pkl', 'rb') as file:
        frames = pickle.load(file)

    while run:
        for n, frame in enumerate(frames):
            w = frame.shape[1]
            h = frame.shape[0]

            scale_percent = 60 # percent of original size
            width  = int(w * scale_percent / 100)
            height = int(h * scale_percent / 100)
            dim = (width, height)
            
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            # cv2.imshow("frame",frame)
            start = time.time()
            detectFace(frame, 
                lambda faceSquare, landmarks, bounding_box   : getEyes(frame, faceSquare, landmarks, bounding_box,
                    lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                        lambda left_coors, right_coors       : print(f"[Processing faces] time elapsed: {time.time() - start}")
                        )
                    )
                )
            
            # start = time.time()
            # calibrationPoints, dataPoints = calibration.getCalibrationData()
            # if calibration.collected():
            #     etracker.fit(calibrationPoints, dataPoints)
            # else:
            #     display.clean()
            #     display.drawPoint(calibration.getPoint(),(0,0,255))
            # display.show()
            # print(f"[Displaying calibration] time elapsed: {time.time() - start}")
            
            if cv2.waitKey(1) == ord('q'):
                run = False
                break                        

            #show point on sandbox
            
    cv2.destroyAllWindows()