
import time 
import math
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

        return self.__interpolatePoints(
                        np.array([(0.95,0.95),
                             (0.05,0.05),
                             (0.95,0.05),
                             (0.05,0.95),
                             (0.5,0.5),
                             (0.5,0.95),
                             (0.95,0.5),
                             (0.5,0.05),
                             (0.05,0.5)]))

    def __interpolatePoints(self,points):
        interpolated = []
        step = 0.005
        for n,point in enumerate(points):
            if n+1 >= len(points):
                break
            
            next_point = points[n+1].copy()
            
            dir_x = math.ceil((next_point[0] - point[0])/abs(next_point[0] - point[0]+0.000001))
            dir_y = math.ceil((next_point[1] - point[1])/abs(next_point[1] - point[1]+0.000001))
            
            interpolated.append(point)
            
            new_point = point.copy()
            while np.linalg.norm(new_point-next_point) > 0.01 and 1.0 > new_point[0] > 0 and 1.0 > new_point[1] > 0:
                new_point[0] = new_point[0] + dir_x * step
                new_point[1] = new_point[1] + dir_y * step
                
                interpolated.append(new_point.copy())

        return np.array(interpolated)



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
