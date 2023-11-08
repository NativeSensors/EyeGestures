import cv2
import dlib
import time
import queue
import pickle
import random
import threading
import numpy as np
from typing import Callable, Tuple
from eyeGestures.utils import VideoCapture
from eyeGestures.face import FaceFinder

if __name__ == "__main__":
    run = True
    display  = CalibrationDisplay()
    etracker = EyeTracker()
    
    vid = VideoCapture('recording/calibrationData1.pkl', 'rb')
    #print("After URL")

    finder = FaceFinder()

    ret = True
    while ret:
        
        ret, frame = vid.read()

        face = finder.find(frame)

        llandmards = face.getLeftEye()
        lpupil = face.getLeftPupil()
        
        # ToDo: write code for detecting eyes positions
        
        if cv2.waitKey(10) == ord('q'):
            run = False
            break                        

            #show point on sandbox
    cv2.destroyAllWindows()