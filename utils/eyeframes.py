import cv2
import math
import numpy as np

class eyeFrame:    
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    LL_EYE = 36
    LR_EYE = 39
    LU_EYE = 37
    LD_EYE = 41

    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye
    RL_EYE = 42
    RR_EYE = 45
    RU_EYE = 43
    RD_EYE = 47

    def __init__(self):
        self.coors = (0,0,2,2)
        self.center = (0.0,0.0)
        self.radius = 0.0
        self.leftEye = None
        self.rightEye = None
        self.landmarks = []
        self.faceImg = None
        self.leftEyeBoundingBox = [0,0,0,0]
        self.rightEyeBoundingBox = [0,0,0,0]

    def setParams(self,orgImage,faceImg, landmarks, coors):
        self.faceImg = faceImg
        self.landmarks = landmarks
        self.coors = coors
        safe_space = 10
        (ox,oy,ow,oh) = coors


        (x,w,y,h) = self.landmarks[[self.LL_EYE,self.LR_EYE,self.LU_EYE,self.LD_EYE]]
        self.leftEyeBoundingBox = [x[0],y[1],w[0]-x[0],h[1]-y[1]]
        (x,y,w,h) = self.leftEyeBoundingBox
        self.leftEye = orgImage[y-safe_space:y+h+safe_space,x-safe_space:x+w+safe_space]
        
        (x,w,y,h) = self.landmarks[[self.RL_EYE,self.RR_EYE,self.RU_EYE,self.RD_EYE]]
        self.rightEyeBoundingBox = [x[0],y[1],w[0]-x[0],h[1]-y[1]]
        (x,y,w,h) = self.rightEyeBoundingBox
        self.rightEye = orgImage[y-safe_space:y+h+safe_space,x-safe_space:x+w+safe_space]
        # print(self.leftEye.shape)

        (x,y,w,h) = self.coors
        self.center = (x+int(w/2),y+int(h/2))
        self.radius = int(w/4)

        pass

    def getCenter(self):
        return self.center
    
    def getLeftEye(self):
        return self.leftEye

    def getRightEye(self):
        return self.rightEye

    def getRadius(self):
        return self.radius

    def getCoors(self):
        return self.coors

    def getFaceImg(self):
        return self.faceImg

    def getLandMarks(self):
        return self.landmarks

    def addFeaturesToImg(self,image):
        (x,y,w,h) = self.coors

        for landmark in self.landmarks:
            # print(/,landmark)
            image = cv2.circle(image, (landmark[0],landmark[1]), 1, (0, 0, 255), 1) 
            
        image = cv2.rectangle(image, (x,y), (x+w,y+h), (255, 0, 0), 2) 
        (x,y,w,h) = self.leftEyeBoundingBox
        image = cv2.rectangle(image, (x,y), (x+w,y+h), (0, 0, 255), 1) 
        (x,y,w,h) = self.rightEyeBoundingBox
        image = cv2.rectangle(image, (x,y), (x+w,y+h), (0, 255, 0), 1) 
        
        (x,y,w,h) = self.coors
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), 5, (0, 255, 255), 5) 
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), int(w/4), (0, 255, 255), 1) 


class faceTracker:

    def __init__(self):
        self.prevFrame = None
        self.nowFrame = eyeFrame()

    def update(self,frame: eyeFrame):
        if(isinstance(self.prevFrame, type(None))):
            self.nowFrame = frame
            self.prevFrame = frame
        else:
            center = frame.getCenter()
            prevCenter = self.prevFrame.getCenter()
            prevRadius = self.prevFrame.getRadius()

            dist = math.sqrt((center[0] - prevCenter[0])**2 + (center[1] - prevCenter[1])**2)
            if dist <= prevRadius:
                self.prevFrame = self.nowFrame
                self.nowFrame = frame

    def getFrame(self):
        return self.nowFrame
            