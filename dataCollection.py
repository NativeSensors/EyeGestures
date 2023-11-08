import cv2
import dlib
import time
import queue
import pickle
import random
import threading
import numpy as np
from eyeGestures.utils import VideoCapture, var
from eyeGestures.face import FaceFinder
from eyeGestures.calibration import Calibration

if __name__ == "__main__":
    cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    
    dataCollection = []
    start = var(True)
    
    (width,height) = (1200,800)
    calibration = Calibration(height, width, 60)
    calibration.start(lambda : start.set(False))
    while start.get():
        #print('About to start the Read command')
        ret, frame = cap.read()
        point = calibration.getTrainingPoint()

        dataCollection.append((point,frame))
        
        cv2.imshow("frame",frame)

        whiteboard = np.full((height, width,3),255,dtype=np.uint8)
        x = int(point[0]*width)
        y = int(point[1]*height)
        cv2.circle(whiteboard,(x,y),4,(0,0,255),10)
    
        cv2.imshow("whiteboard",whiteboard)

        if cv2.waitKey(1) == ord('q'):
            run = False
            break                        

            #show point on sandbox
    cv2.destroyAllWindows()

    fileName = f'recording/calibrationData2.pkl' 
    print(f"saving data to {fileName}")
    with open(fileName, 'wb') as file:
        pickle.dump(dataCollection, file)
    print(f"saved data to {fileName}")
    