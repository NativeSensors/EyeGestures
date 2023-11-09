import cv2
import dlib
import math
import time
import queue
import pickle
import random
import numpy as np
from typing import Callable, Tuple
from eyeGestures.gazeestimator import Gaze
from eyeGestures.calibration import Calibration


class EyeGestures:

    def __init__(self,height,width):
        self.width  = width
        self.height = height

        self.gaze = Gaze()
        self.calibrated = False

        self.calibration = Calibration(self.height, self.width, 60)
        pass

    def __onCalibrated(self):
        self.gaze.fit()
        self.calibrated = True

    def calibrate(self,image):
        if(not self.calibrated and not self.calibration.inProgress()):
            self.calibration.start(self.__onCalibrated)

        point = self.calibration.getTrainingPoint()
        self.gaze.calibrate(point,image)
        
        if len(self.gaze.getCalibration()[0]) > 10:
            self.gaze.fit()
            self.calibrated = True

        return point 

    def getDebugBuffers(self):
        return self.gaze.getDebugBuffers()

    def isCalibrated(self):
        return self.calibrated and not self.calibration.inProgress()

    def estimate(self,image):
        if not self.calibrated:
            return np.full((1,2),np.NAN)
        else:
            return self.gaze.estimate(image)
