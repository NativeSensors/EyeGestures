
import numpy as np
from eyeGestures.utils import Buffor

class EyeProcessor:

    def __init__(self,scale_w=250,scale_h=250):
        self.pupilBuffor = Buffor(20)
        # self.avgRetBuffor = Buffor(20)
        self.scale_w = scale_w
        self.scale_h = scale_h

    def getBuffor(self):
        return self.pupilBuffor.getBuffor()

    def loadBuffor(self,buffor):
        self.pupilBuffor = buffor

    def dumpBuffor(self):
        return self.pupilBuffor

    def append(self,pupil : (int,int) ,landmarks : np.ndarray):
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

        
        self.pupilBuffor.add(
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

    def getAvgPupil(self,width = None, height = None):
        if not width is None and not height is None:
            _retPupil = self.__convertPoint(self.pupilBuffor.getAvg(),
                            width = width,height = height,
                            scale_w = self.scale_w, scale_h = self.scale_h)
        else:
            _retPupil = self.pupilBuffor.getAvg()

        # THIS BUFFOR HAS _retPupil and Width
        # self.avgRetBuffor.add(_retPupil)
        
        return _retPupil

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

            