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
from eyeGestures.face import FaceFinder
from eyeGestures.calibration import GazePredictor, CalibrationData
from eyeGestures.gazeestimator import Gaze

def unison_shuffled_copies(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

def unison_sort_array(a,b):
    assert len(a) == len(b)
    p = np.lexsort((a[:, 1], a[:, 0]))
    return a[p], b[p]

if __name__ == "__main__":
    run = True
    
    fileName = 'recording/calibrationData2.pkl'
    vid = VideoCapture(fileName, 'rb')
    
    gaze = Gaze()

    calibrationPoints = []
    measurement = []

    ret = True
    while ret:
        
        ret, frame = vid.read()
        calibrationPoint, image = frame

        calibrationPoints.append(calibrationPoint)
        measurement.append(image)
    
    # calibrationPoints,measurementPoints = cdata.get()
    
    calibrationPoints,measurement = np.array(calibrationPoints),np.array(measurement)
    calibrationPoints,measurement = unison_shuffled_copies(calibrationPoints,measurement)
    
    division = 400

    trainingCalibrationPoints = calibrationPoints[:division,:]
    trainingMeasurement = measurement[:division,:]

    for n, frame in enumerate(trainingMeasurement):

        gaze.calibrate(trainingCalibrationPoints[n],frame)

    gaze.fit()

    
    testCalibrationPoints = calibrationPoints[division:,:]
    testMeasurement = measurement[division:,:]

    testCalibrationPoints,testMeasurement = unison_sort_array(testCalibrationPoints,testMeasurement)
    # display points and measured points
    
    (width,height) = (1200,800)
    for n, frame in enumerate(testMeasurement):
        whiteboard = np.full((height, width,3),255,dtype=np.uint8)
    
        point = gaze.estimate(frame)

        if not np.isnan(point).any():
        
            testPoint = testCalibrationPoints[n]
            dist = int(math.dist(testPoint, point)*500)
            
            x = int(point[0]*width)
            y = int(point[1]*height)
            cv2.circle(whiteboard,(x,y),4,(dist,0,255-dist),10)
        
            x = int(testPoint[0]*width)
            y = int(testPoint[1]*height)
            cv2.circle(whiteboard,(x,y),4,(0,0,255),10)

            cv2.imshow("whiteboard",whiteboard)
            if cv2.waitKey(100):
                pass

    #show point on sandbox
    cv2.destroyAllWindows()