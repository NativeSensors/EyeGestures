
import cv2
import dlib
import math
import numpy as np
from eyeGestures.utils import Buffor

class EyeProcessor:

    def __init__(self,scale_w=250,scale_h=250):
        self.pupilBuffor = Buffor(20)
        self.avgRetBuffor = Buffor(20)
        self.scale_w = scale_w
        self.scale_h = scale_h

    def append(self,pupil : (int,int) ,landmarks : np.ndarray):
        print("convert")
        # self.pupil = face.getLeftPupil()[0]
        # self.landmarks = face.getLeftEye()
        self.pupil = pupil
        self.landmarks = landmarks

        print("get min and max")
        # get center: 
        self.min_x = np.min(self.landmarks[:,0])
        self.max_x = np.max(self.landmarks[:,0])
        self.min_y = np.min(self.landmarks[:,1])
        self.max_y = np.max(self.landmarks[:,1])

        print("get width and heigh")
        self.width  = self.max_x - self.min_x 
        self.height = self.max_y - self.min_y
        
        print("center")
        self.center = self.__convertPoint(((self.min_x + self.max_x)/2,
                        (self.min_y + self.max_y)/2),
                        width = self.scale_w, height = self.scale_h,
                        scale_w = self.width, scale_h = self.height,
                        offset = (self.min_x, self.min_y))
        
        print("save pupil")
        self.pupilBuffor.add(
            self.__convertPoint(self.pupil,
                            width = self.scale_w, height = self.scale_h,
                            scale_w = self.width, scale_h = self.height,
                            offset = (self.min_x, self.min_y)))

        # do I need that?
        self.height_1 = 20

    def getLeftEyeCorner(self,width = None, height = None):
        newCorner = self.__convertPoint((self.landmarks[1,0],self.landmarks[1,1]),
                        width = self.scale_w, height = self.scale_h,
                        scale_w = self.width, scale_h = self.height,
                        offset = (self.min_x, self.min_y))

        if not width is None and not height is None:
            return self.__convertPoint(newCorner,
                        width = width,height = height,
                        scale_w = self.scale_w, scale_h = self.scale_h)
        else:
            return newCorner

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getCenter(self,width = None, height = None):
        if not width is None and not height is None:
            return self.__convertPoint(self.center,
                        width = width,height = height,
                        scale_w = self.scale_w, scale_h = self.scale_h)
        else:
            return self.center

    def __convertPoint(self,point,width=1.0,height=1.0,scale_w = 1.0,scale_h = 1.0,offset = (0.0,0.0)):
        (min_x, min_y) = offset
        x = int(((point[0]-min_x)/scale_w)*width)
        y = int(((point[1]-min_y)/scale_h)*height)
        return (x,y)

    def getAvgPupil(self,width = None, height = None):
        print("getAvgPupil")
        if not width is None and not height is None:
            _retPupil = self.__convertPoint(self.pupilBuffor.getAvg(),
                            width = width,height = height,
                            scale_w = self.scale_w, scale_h = self.scale_h)
        else:
            _retPupil = self.pupilBuffor.getAvg()

        # THIS BUFFOR HAS _retPupil and Width
        self.avgRetBuffor.add((_retPupil,self.getHeight()))
        
        return (_retPupil,self.getHeight())

## main code:

# self.eyeDisplay.update(face,250,250)
# self.eyeDisplay.draw(whiteboard,image,250,250)
# self.pupilLab.imshow(
#     self.__convertFrame(whiteboard))

###################################################################################3
# get center: 
# whiteboardAdj = np.full((250,250,3),255.0,dtype = np.uint8)


# point = self.pupilBuffor.getAvg()
# x = int(((point[0])/30 - 3.5)*1920)
# y = int(((point[1])/30)*1080)
# self.red_dot_widget.move(x,y)
# print(f"move: {x,y} offset: {min_x,width}")

# # openness need to be calculated relatively to 250x250 frame
# print(f"openness of the eyes: {height} width: {width} scale: {height/width - 0.25}")
# # 0.40 > wide open
# # 0.30 > normally open - looking up or so
# # 0.20 > sligthly closed - looking down

# print(f"vision map: {vision_map_start} {vision_map_wh} {vision_map_end}")
# cv2.rectangle(whiteboardAdj,vision_map_start,vision_map_end,(255,0,0),1)

            