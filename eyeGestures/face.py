import cv2
import dlib
import math
import numpy as np
import eyeGestures.utils as utils
import eyeGestures.eye as eye

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
            print(f"Exception: {e}")
            return None

class Face:

    def __init__(self,image,face):
        self.face = face

        self.landmarks = self._landmarks(self.face)
        self._process(image,self.face)

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

    def _landmarks(self,face):
        landmarks = np.zeros((face.num_parts, 2), dtype=np.dtype)
        for i in range(0, face.num_parts):
            landmarks[i] = (face.part(i).x, face.part(i).y)

        return landmarks

    def _process(self,image,face):
        rect = face.rect
        
        lt_corner = (rect.left(),rect.top())
        rb_corner = (rect.right(),rect.bottom())

        self.eyeLeft  = eye.Eye(image,self.landmarks,0)
        self.eyeRight = eye.Eye(image,self.landmarks,1)
        