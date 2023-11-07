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
        self.run = True
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

    def stop(self):
        self.run = False

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
    frames = []
    run = True
    display = CalibrationDisplay()
    calibration = CalibrationCollector(display.width,display.height,30,10)
    etracker = EyeTracker()
    
    print("videocapture")
    cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    #print("After URL")

    # Get the current time
    start = var(True)
    calibration.start(lambda : start.set(False))
    
    print("starting")
    while start.get():
        #print('About to start the Read command')
        ret, frame = cap.read()
    
        cv2.imshow("frame",frame)
        
        calibrationPoint = calibration.getCalibrationPoint()

        frames.append((calibrationPoint,frame))
        
        display.clean()
        display.drawPoint(calibrationPoint,(0,0,255))
        display.show()

        if cv2.waitKey(1) == ord('q'):
            run = False
            break                        

            #show point on sandbox
    cv2.destroyAllWindows()

    print(f"saving data to calibrationData1.pkl")
    with open(f'recording/calibrationData1.pkl', 'wb') as file:
        pickle.dump(frames, file)
    print(f"saved data to calibrationData1.pkl")
    cap.stop()