
import time 
import math
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class Calibrator:

    def __init__(self,width,height,time = 60):
        self.width = width
        self.height = height
        self.time = time

        self.run = False
        self.t_start = 0

        self.onFinish = None

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
