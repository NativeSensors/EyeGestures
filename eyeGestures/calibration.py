
import time 
import numpy as np

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

        return np.array([(0.8,0.8),
                             (0.2,0.2),
                             (0.8,0.2),
                             (0.2,0.8),
                             (0.5,0.5),
                             (0.5,0.8),
                             (0.8,0.5),
                             (0.5,0.2),
                             (0.2,0.5)])

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
            
            print(f"index: {index}")
            if(index < 0 or index >= len(self.points)):
                self.run = False

                if not self.onFinish is None:
                    self.onFinish()
                    return self.points[0]
                
            return self.points[index]
