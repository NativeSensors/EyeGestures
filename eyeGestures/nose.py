
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
    NOSE_CENTER = [1]
    
    def __init__(self,image : np.ndarray, landmarks : list, boundaries: np.ndarray):
        self.image = image

        self._process(self.image,landmarks,boundaries)
        #getting polar coordinates

    def getCenter(self):
        return self.center

    def getHeadTiltOffset(self):
        x,y,w,h = self.boundaries

        w_limit = w/2
        h_limit = h/2 

        tilt = np.array(((self.dist2left - w_limit),(self.dist2top - h_limit))) 
        return tilt
    
    def _process(self,image,landmarks,boundaries):
        self.boundaries = boundaries
        x,y,w,h = self.boundaries

        self.center = np.array(landmarks[self.NOSE_CENTER], dtype=np.int32) - np.array((x,y))
        print(self.center)
        print("boundaries: ", x,y,w,h, self.center, np.array((x,y)))

        self.dist2left    = self.center[0,0]
        self.dist2right   = w - self.center[0,0]
        self.dist2top     = self.center[0,1]
        self.dist2bottom  = h - self.center[0,1]