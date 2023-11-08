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
from eyeGestures.gazeestimator import Gaze


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
        self.gaze.estiamte(point,image)

        return point 

    def isCalibrated(self):
        return self.calibrated

    def gaze(self,image):
        if not self.calibrated:
            return np.full((1,2),np.NAN)
        else:
            return self.gaze.estiamte(image)
