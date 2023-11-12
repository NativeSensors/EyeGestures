
import cv2
import math
import numpy as np

class Nose:    
    NOSE_KEYPOINTS = [28, 29, 30, 31, 32, 33 ,34, 35, 36] # keypoint indices for left eye
    NOSE_CENTER = [31]
    LEFT_EDGE   = [3]
    RIGHT_EDGE  = [15]
    BOTTOM_EDGE = [9]
    TOP_EDGE    = [28]
    
    def __init__(self,image : np.ndarray, landmarks : list):
        self.image = image
        
        self._process(self.image,landmarks)
        #getting polar coordinates

    def getCenter(self):
        return self.center

    def getLandmarks(self):
        return self.landmarks 

    def getcenterDist(self):
        return self.centerDist

    def getLeftRightDists(self):
        return np.array([self.dist2left,self.dist2right])

    def _process(self,image,landmarks):
        self.left   = np.array(landmarks[self.LEFT_EDGE], dtype=np.int32)
        self.right  = np.array(landmarks[self.RIGHT_EDGE], dtype=np.int32)
        self.bottom = np.array(landmarks[self.BOTTOM_EDGE], dtype=np.int32)
        self.top    = np.sum(np.array(landmarks[self.TOP_EDGE], dtype=np.int32))/len(self.TOP_EDGE)
        
        
        self.center = np.array(landmarks[self.NOSE_CENTER], dtype=np.int32)
        
        self.dist2left  = np.linalg.norm(self.left-self.center)
        self.dist2right = np.linalg.norm(self.right-self.center)
        self.dist2bottom  = np.linalg.norm(self.bottom-self.center)
        self.dist2top     = np.linalg.norm(self.top-self.center)

        self.centerDist = (self.dist2left/(self.dist2left + self.dist2right),
                           self.dist2bottom/(self.dist2bottom + self.dist2top))


        # overwritting landmarks
        self.landmarks = np.array(landmarks[self.NOSE_KEYPOINTS], dtype=np.int32)
        pass