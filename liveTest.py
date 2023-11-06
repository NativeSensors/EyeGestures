import cv2
import dlib
import time
import queue
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


    
def processPoints(calibrator,tracker,points):

    if not calibrator.collected():
        calibration.collect(points)
        return [0.0,0.0]
    else:
        display.clean()
        return tracker.predict(points)

if __name__ == "__main__":
    frames = []
    run = True
    display = CalibrationDisplay()
    calibration = CalibrationCollector(display.width,display.height)
    etracker = EyeTracker()
    
    cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    #print("After URL")

    frames = []
    # Get the current time
    while True:
        
        #print('About to start the Read command')
        ret, frame = cap.read()
    
        w = frame.shape[1]
        h = frame.shape[0]

        scale_percent = 20 # percent of original size
        width  = int(w * scale_percent / 100)
        height = int(h * scale_percent / 100)
        dim = (width, height)
        
        frame_display = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow("frame",frame_display)

        detectFace(frame, 
            lambda faceSquare, landmarks, bounding_box   : getEyes(frame, faceSquare, landmarks, bounding_box,
                lambda left_eye_region, right_eye_region : getCoordinates(left_eye_region, right_eye_region, 
                    lambda left_coors, right_coors       : display.drawPoint(processPoints(calibration,etracker,left_coors),(255,0,0))
                    )
                )
            )
        
        calibrationPoints, dataPoints = calibration.getCalibrationData()
        print(f"calibrationPoints:{calibrationPoints.shape} dataPoints:{dataPoints.shape}")
        if calibration.collected():
            etracker.fit(calibrationPoints, dataPoints)
        else:
            display.clean()
            display.drawPoint(calibration.getPoint(),(0,0,255))
        display.show()
        if cv2.waitKey(1) == ord('q'):
            run = False
            break                        

            #show point on sandbox
            
    cv2.destroyAllWindows()