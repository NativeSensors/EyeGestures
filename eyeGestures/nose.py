
import cv2
import math
import numpy as np
from eyeGestures.utils import Buffor 

class NoseDirection:

    def __init__(self):
        self.__tmp__buffor = Buffor(5)
        self.__tmp__mapped_nose_buffor = Buffor(20)
        self.min_nose_x = 1.0
        self.min_nose_y = 1.0
        self.max_nose_x = 0.0
        self.max_nose_y = 0.0
        self.min_mapped_nose_x = 1.0
        self.min_mapped_nose_y = 1.0
        self.max_mapped_nose_x = 0.0
        self.max_mapped_nose_y = 0.0
        
    def __set_lim_nose(self,avg):
        (avg_nose_x,avg_nose_y) = avg
        self.min_nose_x = avg_nose_x if avg_nose_x < self.min_nose_x else self.min_nose_x
        self.min_nose_y = avg_nose_y if avg_nose_y < self.min_nose_y else self.min_nose_y
        self.max_nose_x = avg_nose_x if avg_nose_x > self.max_nose_x else self.max_nose_x
        self.max_nose_y = avg_nose_y if avg_nose_y > self.max_nose_y else self.max_nose_y
    
    def __get_mapped_nose(self,avg_nose):
        (avg_nose_x,avg_nose_y) = avg_nose
        return (avg_nose_x/(self.max_nose_x - self.min_nose_x),
                    avg_nose_y/(self.max_nose_y - self.min_nose_y))

    def __set_lim_mapped(self,mapped_nose):
        self.min_mapped_nose_x = mapped_nose[0] if mapped_nose[0] < self.min_mapped_nose_x else self.min_mapped_nose_x
        self.min_mapped_nose_y = mapped_nose[1] if mapped_nose[1] < self.min_mapped_nose_y else self.min_mapped_nose_y
        self.max_mapped_nose_x = mapped_nose[0] if (mapped_nose[0] > self.max_mapped_nose_x) and (mapped_nose[0] < 1.2) else self.max_mapped_nose_x
        self.max_mapped_nose_y = mapped_nose[1] if (mapped_nose[1] > self.max_mapped_nose_y) and (mapped_nose[1] < 1.2) else self.max_mapped_nose_y
        
    def getPos(self,nose):
        nose_center = nose.getcenterDist()
            
        self.__tmp__buffor.add(nose_center)

        avg_nose = self.__tmp__buffor.getAvg()
        if self.__tmp__buffor.getLen() >= 5:
            self.__set_lim_nose(avg_nose)
            
            mapped_nose = self.__get_mapped_nose(avg_nose)
            self.__tmp__mapped_nose_buffor.add(mapped_nose)
            if self.__tmp__mapped_nose_buffor.getLen() >= 20:
                self.__set_lim_mapped(mapped_nose)
                return np.array([mapped_nose[0] - self.min_mapped_nose_x, mapped_nose[1]-self.min_mapped_nose_y])
                
                # print(f"dnose: max: {self.max_dnose_x,self.max_dnose_y} min: {self.min_dnose_x,self.min_dnose_y}")
        return np.full((1,2),np.NAN)

class Nose:    
    # Indecies are one smaller than the landmarks documentation due to indexing starting from 1
    NOSE_KEYPOINTS = [27, 28, 29, 30, 31, 32 ,33, 34, 35] # keypoint indices for nose
    NOSE_CENTER = [30]
    NOSE_LEFT_RIGHT = [31,35]
    LEFT_EDGE   = [2]
    RIGHT_EDGE  = [15]
    BOTTOM_EDGE = [8]
    TOP_EDGE    = [27]
    
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

    def getHeadTilt(self):
        return self.headTilt

    def __headTilt(self,landmarks):
        leftPoint  = landmarks[self.NOSE_LEFT_RIGHT[0]]
        rightPoint = landmarks[self.NOSE_LEFT_RIGHT[1]]
        x = (rightPoint[0] - leftPoint[0])  
        y = (rightPoint[1] - leftPoint[1])  
        print(f"x,y : {x},{y} point l: {leftPoint} point r: {rightPoint}")

        return math.atan2(y,x) * 180/math.pi

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

        self.headTilt = self.__headTilt(landmarks)

        self.centerDist = (self.dist2left/(self.dist2left + self.dist2right),
                           self.dist2bottom/(self.dist2bottom + self.dist2top))


        # overwritting landmarks
        self.landmarks = np.array(landmarks[self.NOSE_KEYPOINTS], dtype=np.int32)
        pass