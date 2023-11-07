import matplotlib.pyplot as plt
import numpy as np
import random
import pickle
import math
import time
import cv2

from typing import Callable, Tuple
from screeninfo import get_monitors
from utils.eyeframes import eyeFrame, faceTracker
from sklearn.linear_model import LinearRegression
## Input:  Face image
## Output: eye point

# def getFeature():

class pupilDetector():
    def __init__(self, _img):
        self._img = _img
        self._pupil = None

    def detect_pupil (self):
        inv = cv2.bitwise_not(self._img)
        thresh = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
        
        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(thresh,kernel,iterations = 1)
        
        ret,thresh1 = cv2.threshold(erosion,220,255,cv2.THRESH_BINARY)
        cnts, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        center = (0,0)
        radius = 0
        if len(cnts) != 0:
            c = max(cnts, key = cv2.contourArea)
            (x,y),radius = cv2.minEnclosingCircle(c)
            center = (int(x),int(y))
            radius = int(radius)
            # cv2.circle(self._img,center,radius,(255,0,0),2)

        return (center,radius)


class EyeSink:

    def __init__(self):
        self.frame_prev = None
        self.frame_now = None
        pass

    def push(self,frame : np.ndarray) -> np.ndarray:
        (cX, cY) = self.getCenter(frame)
        return np.array((cX, cY))

        pass

    def getCenter(self,frame : np.ndarray) -> np.ndarray:
        # Convert the frame to grayscale if it's a color image
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find the minimum and maximum values in the grayscale frame
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_frame)

        frame_scaled = np.uint8((frame / max_val)*200)
        # self.frame_now = cv2.convertScaleAbs(frame, 10, 1)

        id = pupilDetector(frame_scaled)
        gray_frame = cv2.cvtColor(frame_scaled, cv2.COLOR_BGR2GRAY)

        (center,radius) = id.detect_pupil()

        
        # frame_show = cv2.cvtColor(frame,cv2.COLOR_GRAY2RGB)
        (height, width, colours) = frame_scaled.shape
        # (x_center,y_center) = (0,0)
        (x_center,y_center) = center

        return (x_center/width,y_center/height)
        pass

class EyeTracker:

    def __init__(self):
        # Create a linear regression model
        self.model = LinearRegression()
        self.calibrated = False
        pass

    def predict(self,points):
        if self.calibrated:
            points_reshaped = points.reshape(1, -1)
            predicted_y = self.model.predict(points_reshaped)
            return predicted_y[0]
        else:
            print("returning 0")
            return [0.0,0.0]

    def fit(self,calibrationPoints, dataPoints):
        dataPoints_reshaped = dataPoints.reshape(dataPoints.shape[0], -1)
        self.model.fit(dataPoints_reshaped, calibrationPoints)
        self.calibrated = True


class CalibrationCollector:

    def __init__(self, width, height):
        self.calibrationTimeLimit = 60 #s
        self.calibrationPeriod = 5 # s
        self.__start = False
        self.collectedPoints = []
        self.calibrationPoints = []

        self.width  = width 
        self.height = height

        for _ in range(int(self.calibrationTimeLimit/self.calibrationPeriod)):
            y = random.randint(1, self.width - 1)/self.width
            x = random.randint(1, self.height - 1)/self.height
            self.calibrationPoints.append((x, y))

        self.calibrationStart_t = 0
        self.currentCalibrationPoint = len(self.calibrationPoints) - 1
        self.onFinish = None

    def start(self, onFinish):
        self.onFinish = onFinish
        self.__start = True
        self.calibrationStart_t = time.time()

    def getCalibrationPoint(self) -> (float,float):
        index = 0
        if self.__start:
            index = int((self.calibrationTimeLimit - (time.time() - self.calibrationStart_t)) / self.calibrationPeriod)
            if( index < 0):
                if self.onFinish: 
                    self.onFinish()
                self.__start = False
                return self.calibrationPoints[0]
        print(index,len(self.calibrationPoints))
        return self.calibrationPoints[index]

class CalibrationDisplay:

    def __init__(self):
        monitor = get_monitors()[0]
        self.width  = int(monitor.width * 0.8)
        self.height = int(monitor.height * 0.8)
        self.display = np.zeros((self.height, self.width,3))
        self.display.fill(255)

    def clean(self):
        self.display.fill(255)

    def drawPoint(self, point, colour):
        cv2.circle(self.display , (int(point[0]*self.width),int(point[1]*self.height)) , 10, colour, -1)
        
    def show(self):
        cv2.imshow("display",self.display)