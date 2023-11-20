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

    # Relative postions to face bounding box  
    # def __relativePos(self,positions):
    #     left, top = self.rect.left(), self.rect.top()
    #     relPositions = positions
    #     relPositions[:,0] = relPositions[:,0] - left
    #     relPositions[:,1] = relPositions[:,1] - top
    #     return relPositions

    # Absolute postions to image
    # def getBoundingBox(self):
    #     return np.array([[self.rect.left(),self.rect.top()],
    #                     [self.rect.right(),self.rect.bottom()]])

    def getLeftEye(self):
        return self.eyeLeft

    def getRightEye(self):
        return self.eyeRight

    def getLandmarks(self):
        return self.landmarks

    # def getHeadTilt(self):
    #     return self.nose.getHeadTilt()

    # def getNose(self):
    #     return self.nose

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

        # LEGACY:
        # landmarks = np.zeros((face.num_parts, 2), dtype=np.dtype)
        # for i in range(0, face.num_parts):
        #     landmarks[i] = (face.part(i).x, face.part(i).y)

        return np.array(__face_landmarks)

    def _process(self,image,face):
        # self.rect = face.rect

        if not hasattr(self,"eyeLeft"):
            self.eyeLeft  = eye.Eye(image,self.landmarks,0)
        else:
            self.eyeLeft.update(image,self.landmarks)

        if not hasattr(self,"eyeRight"):
            self.eyeRight  = eye.Eye(image,self.landmarks,1)
        else:
            self.eyeRight.update(image,self.landmarks)

        # self.nose = nose.Nose(image,self.landmarks)
        