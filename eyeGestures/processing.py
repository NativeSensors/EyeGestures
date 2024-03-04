
import numpy as np
from eyeGestures.utils import Buffor

class EyeProcessor:

    def __init__(self,scale_w=250,scale_h=250):
        self.scale_w = scale_w
        self.scale_h = scale_h


    def append(self,pupil : (int,int) ,landmarks : np.ndarray, pupilBuffor):
        self.pupil = pupil
        self.landmarks = landmarks

        # get center: 
        margin = 5
        self.min_x = np.min(self.landmarks[:,0]) - margin
        self.max_x = np.max(self.landmarks[:,0]) + margin
        self.min_y = np.min(self.landmarks[:,1]) - margin
        self.max_y = np.max(self.landmarks[:,1]) + margin
        
        assert(self.pupil[0] > self.min_x)
        assert(self.pupil[1] > self.min_y)

        width  = self.max_x - self.min_x
        height = (self.max_y - self.min_y)/2

        
        pupilBuffor.add(
            self.__convertPoint(self.pupil,
                        width = self.scale_w, height = self.scale_h,
                        scale_w = width, scale_h = height,
                        offset = (self.min_x, self.min_y)))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def __convertPoint(self, point, width=1.0, height=1.0, scale_w = 1.0, scale_h = 1.0, offset = (0.0,0.0)):
        (min_x, min_y) = offset
        x = int(((point[0]-min_x)/scale_w)*width)
        y = int(((point[1]-min_y)/scale_h)*height)
        return (x,y)

    def getAvgPupil(self, width, height, pupilBuffor):
        if not width is None and not height is None:
            _retPupil = self.__convertPoint(pupilBuffor.getAvg(),
                            width = width,height = height,
                            scale_w = self.scale_w, scale_h = self.scale_h)
        else:
            _retPupil = pupilBuffor.getAvg()

        # THIS BUFFOR HAS _retPupil and Width
        # self.avgRetBuffor.add(_retPupil)
        
        return _retPupil

## main code:
