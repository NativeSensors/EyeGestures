import cv2
import dlib
import math
import numpy as np
import eyeGestures.eye as eye
import eyeGestures.nose as nose

class FaceFinder:

    def __init__(self):
        self.facePredictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        self.faceDetector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def find(self,image):
        if len(image.shape) > 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        try:
            (x, y, w, h) = self.faceDetector.detectMultiScale(image, 1.1, 9)[0]
            face = self.facePredictor(image, dlib.rectangle(x, y, x+w, y+h))
        
            return Face(image,face)
        except Exception as e:
            print(f"Exception in FaceFinder: {e}")
            return None

class Face:

    def __init__(self,image,face):
        self.face = face

        self.landmarks = self._landmarks(self.face)
        print(f"processing face self.landmarks:{self.landmarks.shape}")
        self._process(image,self.face)

    # Relative postions to face bounding box  
    def __relativePos(self,positions):
        left, top = self.rect.left(), self.rect.top()
        relPositions = positions
        relPositions[:,0] = relPositions[:,0] - left
        relPositions[:,1] = relPositions[:,1] - top
        return relPositions

    def getRelLeftEye(self):
        return self.__relativePos(
            self.eyeLeft.getLandmarks())
        
    def getRelRightEye(self):
        return self.__relativePos(
            self.eyeRight.getLandmarks())

    def getRelLeftPupil(self):
        return self.__relativePos(
            self.eyeLeft.getPupil())

    def getRelRightPupil(self):
        return self.__relativePos(
            self.eyeRight.getPupil())

    # Absolute postions to image
    def getBoundingBox(self):
        return np.array([[self.rect.left(),self.rect.top()],
                        [self.rect.right(),self.rect.bottom()]])

    def getLeftEye(self):
        return self.eyeLeft.getLandmarks()

    def getRightEye(self):
        return self.eyeRight.getLandmarks()

    def getLeftPupil(self):
        return self.eyeLeft.getPupil()

    def getRightPupil(self):
        return self.eyeRight.getPupil()

    def getLandmarks(self):
        return self.landmarks

    def getLeftPolar(self):
        return self.eyeLeft.getPolar()

    def getRightPolar(self):
        return self.eyeRight.getPolar()

    def getNoseFeatures(self):
        return self.nose

    def getLandmarks(self):
        return self.landmarks
        
    def _landmarks(self,face):
        landmarks = np.zeros((face.num_parts, 2), dtype=np.dtype)
        for i in range(0, face.num_parts):
            landmarks[i] = (face.part(i).x, face.part(i).y)

        return landmarks

    def _process(self,image,face):
        self.rect = face.rect
        
        self.lt_corner = (self.rect.left(),self.rect.top())
        self.rb_corner = (self.rect.right(),self.rect.bottom())

        self.eyeLeft  = eye.Eye(image,self.landmarks,0)
        self.eyeRight = eye.Eye(image,self.landmarks,1)
        self.nose     = nose.Nose(image,self.landmarks)
        