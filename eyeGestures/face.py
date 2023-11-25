import cv2
import dlib
import math
import numpy as np
import mediapipe as mp
import eyeGestures.eye as eye
import eyeGestures.nose as nose

class FaceFinder:

    def __init__(self):
        self.facePredictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        self.faceDetector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    def find(self,image):

        assert(len(image.shape) > 2)
        # if len(image.shape) > 2:
        #     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        try:
            # LEGACY:
            # (x, y, w, h) = self.faceDetector.detectMultiScale(image, 1.1, 9)[0]
            # __face_landmarks = self.facePredictor(image, dlib.rectangle(x, y, x+w, y+h))
        
            face = self.mp_face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
 
            # if attrirbute do not exist then create it
            if not hasattr(self,"face"):
                self.face = Face(image,face)
            else:
                self.face.update(image,face)

            return self.face
        except Exception as e:
            print(f"Exception in FaceFinder: {e}")
            return None

class Face:

    def __init__(self,image,face):
        self.face = face
        self.image_h, self.image_w, _ = image.shape
        
        self.landmarks = self._landmarks(self.face)
        self._process(image,self.face)

    def update(self,image,face):
        self.face = face

        self.landmarks = self._landmarks(self.face)
        self._process(image,self.face)

    def getBoundingBox(self):
        margin = 0
        min_x = np.min(self.landmarks[:,0]) - margin
        max_x = np.max(self.landmarks[:,0]) + margin
        min_y = np.min(self.landmarks[:,1]) - margin
        max_y = np.max(self.landmarks[:,1]) + margin
        
        width  = int((max_x - min_x)/2)
        height = int((max_y - min_y)/2)

        return (min_x,min_y,width,height)

    def getLeftEye(self):
        return self.eyeLeft

    def getRightEye(self):
        return self.eyeRight

    def getLandmarks(self):
        return self.landmarks

    def getLandmarks(self):
        return self.landmarks
        
    def _landmarks(self,face):
                   
        __complex_landmark_points = face.multi_face_landmarks
        __complex_landmarks = __complex_landmark_points[0].landmark

        __face_landmarks = []
        for landmark in __complex_landmarks:
            __face_landmarks.append((
                landmark.x * self.image_w,
                landmark.y * self.image_h))

        return np.array(__face_landmarks)

    def _process(self,image,face):
        if not hasattr(self,"eyeLeft"):
            self.eyeLeft  = eye.Eye(image,self.landmarks,0)
        else:
            self.eyeLeft.update(image,self.landmarks)

        if not hasattr(self,"eyeRight"):
            self.eyeRight  = eye.Eye(image,self.landmarks,1)
        else:
            self.eyeRight.update(image,self.landmarks)

        # self.nose = nose.Nose(image,self.landmarks)
        