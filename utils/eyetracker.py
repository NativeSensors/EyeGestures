import numpy as np
import math
import cv2
## Input:  Face image
## Output: eye point


# def getFeature():

class pupil_detection():
    def __init__(self, _img):
        self._img = _img
        self._pupil = None

    def detect_pupil (self):
        inv = cv2.bitwise_not(self._img)
        thresh = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(thresh,kernel,iterations = 1)
        ret,thresh1 = cv2.threshold(erosion,220,255,cv2.THRESH_BINARY)
        cnts, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        center = (0,0)
        radius = 0
        if len(cnts) != 0:
            c = max(cnts, key = cv2.contourArea)
            (x,y),radius = cv2.minEnclosingCircle(c)
            center = (int(x),int(y))
            radius = int(radius)
            # cv2.circle(self._img,center,radius,(255,0,0),2)

        return (center,radius)


class EyeSink:

    def __init__(self):
        self.frame_prev = None
        self.frame_now = None
        pass

    def push(self,frame : np.ndarray) -> np.ndarray:
        (cX, cY) = self.getCenter(frame)
        # (cX, cY) = self.getCenterOpticalFlow(frame)
        return (cX, cY)

        pass

    def getCenter(self,frame : np.ndarray) -> np.ndarray:

        self.frame_now = frame
        # Convert the frame to grayscale if it's a color image
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find the minimum and maximum values in the grayscale frame
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_frame)

        self.frame_now = (self.frame_now / max_val)*200
        self.frame_now = np.uint8(self.frame_now)
        # self.frame_now = cv2.convertScaleAbs(frame, 10, 1)

        id = pupil_detection(self.frame_now)
        gray_frame = cv2.cvtColor(self.frame_now, cv2.COLOR_BGR2GRAY)

        (center,radius) = id.detect_pupil()

        
        # frame_show = cv2.cvtColor(frame,cv2.COLOR_GRAY2RGB)
        (height, width, colours) = self.frame_now.shape
        # (x_center,y_center) = (0,0)
        (x_center,y_center) = center

        return (x_center/width,y_center/height)
        pass