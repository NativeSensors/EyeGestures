
import time 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class GazePredictor:

    def __init__(self):
        self.model = LinearRegression()
        pass

    def train(self,eyes,calibrations):
        eyes = eyes.reshape(eyes.shape[0], -1)
        self.model.fit(eyes, calibrations)

    def predict(self,eye):
        eye = eye.reshape(1,eye.shape[0]*eye.shape[1])
        point = self.model.predict(eye)
        
        return point[0]

class CalibrationData:

    def __init__(self):
        self.calibrationPoints = []
        self.measuredPoints = []

    def add(self,calibrationPoint,measuredPoint):
        if not np.isnan(calibrationPoint).any() and not np.isnan(measuredPoint).any():
            self.calibrationPoints.append(calibrationPoint)
            self.measuredPoints.append(measuredPoint)
    
    def get(self):
        return np.array(self.calibrationPoints), np.array(self.measuredPoints)

class Calibration:

    def __init__(self,width,height,time = 60):
        self.width = width
        self.height = height
        self.time = time
        self.points = self.__calibrationPoints()

        self.run = False
        self.t_start = 0

        self.onFinish = None


    def __calibrationPoints(self):

        return np.array([(0.95,0.95),
                             (0.05,0.05),
                             (0.95,0.05),
                             (0.05,0.95),
                             (0.5,0.5),
                             (0.5,0.95),
                             (0.95,0.5),
                             (0.5,0.05),
                             (0.05,0.5)])

    def start(self,onFinish):
        self.t_start = time.time()
        self.run = True

        self.onFinish = onFinish

    def getTrainingPoint(self):

        if not self.run:
            return self.points[0]
        
        else:
            time_step = self.time/len(self.points)
            index = int((time.time() - self.t_start)/time_step) * ((time.time() - self.t_start) > 0)
            
            if(index < 0 or index >= len(self.points)):
                self.run = False

                if not self.onFinish is None:
                    self.onFinish()
                    return self.points[0]
                
            return self.points[index]

    def inProgress(self):
        return self.run 
