import cv2
import dlib
import time
import pickle
import random
from screeninfo import get_monitors
import numpy as np
from typing import Callable, Tuple
from utils.eyeframes import eyeFrame, faceTracker
from utils.eyetracker import EyeSink
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from utils.utils import detectFace, getEyes, getCoordinates

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
        self.calibrationTimeLimit = 25 #s
        self.calibrationPeriod = 1 # s
        self.start = False
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
        pass

    def collect(self,point):
        if len(self.collectedPoints) == 0:
            self.start = True
            self.calibrationStart_t = time.time()

        if self.start:
            self.collectedPoints.append((self.calibrationPoints[self.currentCalibrationPoint], point))
            print(time.time() - self.calibrationStart_t)
            if (self.calibrationTimeLimit - (time.time() - self.calibrationStart_t)) >= 0:
                self.currentCalibrationPoint = int((self.calibrationTimeLimit - (time.time() - self.calibrationStart_t)) / self.calibrationPeriod)
            else:
                self.start = False

    def getPoint(self):
        return (self.calibrationPoints[self.currentCalibrationPoint][0],
                self.calibrationPoints[self.currentCalibrationPoint][1])

    def getCalibrationData(self) -> (np.ndarray,np.ndarray):
        
        __calibrationPoints = []
        __dataPoints = []
        for calibrationPoint, points in self.collectedPoints:
            __calibrationPoints.append(calibrationPoint)
            __dataPoints.append(points)
        
        return (np.array(__calibrationPoints),np.array(__dataPoints))
    
    def collected(self):
        return (self.calibrationStart_t > 0) and not self.start

class CalibrationDisplay:

    def __init__(self):
        monitor = get_monitors()[1]
        self.width  = int(monitor.width * 0.8)
        self.height = int(monitor.height * 0.8)
        self.display = np.zeros((self.width, self.height,3))
        self.display.fill(255)

        # cv2.namedWindow("display", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("display",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    def clean(self):
        self.display.fill(255)

    def drawPoint(self, point, colour):
        print(f"self display point {point} scaled points: {int(point[0]*self.width),int(point[1]*self.height)} max: {(self.width,self.height)}")
        cv2.circle(self.display , (int(point[0]*self.width),int(point[1]*self.height)) , 10, colour, -1)
        
    def show(self):
        cv2.imshow("display",self.display)

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