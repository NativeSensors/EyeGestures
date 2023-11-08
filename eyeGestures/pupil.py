import cv2
import math
import numpy as np
import eyeGestures.utils as utils

class Pupil:

    def __init__(self,eye_frame,ref_x, ref_y):
        self.thersh = 35
        self.eye_frame = eye_frame
        self.ref_x = ref_x
        self.ref_y = ref_y

        self.__process(eye_frame)

    def getCoords(self):
        return self.pupil

    def _getIris(self,eye_frame,threshold):

        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(eye_frame, 5, 5, 10)
        new_frame = cv2.erode(new_frame, kernel, iterations=1)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]
        
        return new_frame

    def _findIris(self,eye_frame):
        #Find best Iris cadidate
        swipe = 5
        start = (self.thersh - swipe) * (self.thersh - swipe) >= 0
        end = 100
        self.irisCandidated = []

        for threshold in range(start,end,swipe):
            iris = self._getIris(eye_frame,threshold)
            if self._sizeIris(iris) > 0.045:
                self.thersh = threshold
                break
            self.irisCandidated.append(iris)
        
        return iris

    def _sizeIris(self,iris):
        h, w = iris.shape
        w_pixels = cv2.countNonZero(iris)
        all_pixels = h*w

        # percentage of black pixels
        pb_pixels = 1.00 - w_pixels/all_pixels

        return pb_pixels

    def __process(self,eye_frame):
        
        iris = self._findIris(eye_frame)
        contours, _ = cv2.findContours(iris, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea)

        try:
            moments = cv2.moments(contours[-2])
            x = int(moments['m10'] / moments['m00']) 
            y = int(moments['m01'] / moments['m00'])

            self.pupil = np.array([(x + self.ref_x,y + self.ref_y)])
        except (IndexError, ZeroDivisionError):
            self.pupil = np.array([(np.NAN,np.NAN)])
            pass
