import numpy as np
import cv2
## Input:  Face image
## Output: eye point


# def getFeature():

class EyeSink:

    def __init__(self):
        pass

    def push(self,frame : np.ndarray) -> np.ndarray:
        (cX, cY) = self.getCenter(frame)
        return (cX, cY)

        pass

    def getCenter(self,frame : np.ndarray) -> np.ndarray:
        _,frame_thresh = cv2.threshold(frame, 40, 250 ,cv2.THRESH_BINARY)
        
        x_center = 0
        y_center = 0
        N = 0
        for row, pixels_row in enumerate(frame_thresh):
            for col, pixel in enumerate(pixels_row):
                if pixel == 0:
                    x_center += col
                    y_center += row        
                    N += 1
        
        if N > 0:
            x_center = int(x_center / N)
            y_center = int(y_center / N)
        
        return (x_center,y_center)
        pass