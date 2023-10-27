import cv2
import math
import numpy as np

class eyeFrame:    

    def __init__(self):
        self.coors = (0,0,2,2)
        self.center = (0.0,0.0)
        self.radius = 0.0
        self.leftEye = None
        self.rightEye = None
        self.landmarks = []
        self.faceImg = None

    def setParams(self,faceImg, landmarks, coors):
        self.faceImg = faceImg
        self.landmarks = landmarks
        self.coors = coors
        (x,y,w,h) = self.coors

        self.leftEye  = faceImg[:int(w/2),int(h/2):]
        self.rightEye = faceImg[:int(w/2),:int(h/2)]        

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
        image = cv2.rectangle(image, (x,y), (x+int(w/2),y+int(h/2)), (0, 0, 255), 2) 
        image = cv2.rectangle(image, (x+int(w/2),y), (x+w,y+int(h/2)), (0, 255, 0), 2) 
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), 5, (0, 255, 255), 5) 
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), int(w/4), (0, 255, 255), 1) 


class faceTracker:

    def __init__(self):
        self.prevFrame = None
        self.nowFrame = eyeFrame()

    def update(self,frame: eyeFrame):
        if(isinstance(self.prevFrame, type(None))):
            print(f"first update {self.prevFrame} and {self.nowFrame}")
            self.nowFrame = frame
            self.prevFrame = frame
            print(f"first update {self.prevFrame} and {self.nowFrame}")
            
        else:
            center = frame.getCenter()
            prevCenter = self.prevFrame.getCenter()
            prevRadius = self.prevFrame.getRadius()

            dist = math.sqrt((center[0] - prevCenter[0])**2 + (center[1] - prevCenter[1])**2)
            print(f"{dist} , {prevRadius} : x:{center[0]} y:{center[1]} px:{prevCenter[0]} py:{prevCenter[1]}")
            if dist <= prevRadius:
                print("update")
                self.prevFrame = self.nowFrame
                self.nowFrame = frame

    def getFrame(self):
        return self.nowFrame
            