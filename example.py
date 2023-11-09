import cv2
import dlib
import math
import time
import queue
import pickle
import random
import threading
import numpy as np
from typing import Callable, Tuple
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

from screeninfo import get_monitors


if __name__ == "__main__":    
    cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    
    monitors = get_monitors()
    (width,height) = (int(monitors[0].width*0.8),int(monitors[0].height*0.8))
    gestures = EyeGestures(height,width)
    
    ret = True
    while ret:
        whiteboard = np.full((height, width,3),255,dtype=np.uint8)
        
        ret, frame = cap.read()
        
        if not gestures.isCalibrated():
            cPoint = gestures.calibrate(frame)
            ePoint = gestures.estimate(frame)     
        
            x = int(cPoint[0]*width)
            y = int(cPoint[1]*height)
            cv2.circle(whiteboard,(x,y),4,(0,0,255),4)
            
        else:
            ePoint = gestures.estimate(frame)     


        if not np.isnan(ePoint).any():
            x = int(ePoint[0]*width)
            y = int(ePoint[1]*height)
            cv2.circle(whiteboard,(x,y),4,(255,0,0),4)
        
        cv2.imshow("whiteboard",whiteboard)
        if cv2.waitKey(1) == ord('q'):
            pass


    #show point on sandbox
    cv2.destroyAllWindows()