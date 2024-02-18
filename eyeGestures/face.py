import cv2
import numpy as np
import mediapipe as mp
import eyeGestures.eye as eye
import eyeGestures.nose as nose
from eyeGestures.contexter import Contexter 

class FaceFinder:

    def __init__(self, static_image_mode = True):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            static_image_mode=static_image_mode,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.contexter = Contexter()

    def find(self,image,context_id):

        assert(len(image.shape) > 2)

        try:
            face_mesh = self.mp_face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
 
            # if attrirbute do not exist then create it
            # if not hasattr(self,"face"):
            #     self.face = Face(image,face)
            # else:
            #     self.face.update(image,face)
            face = self.contexter.get_context(context_id,Face(image,face_mesh))
            face.update(image,face_mesh)
            
            return face
        except Exception as e:
            print(f"Exception in FaceFinder: {e}")
            return None

    def get_contextes(self):
        return self.contexter.get_number_contextes()

class Face:

    def __init__(self,image,face):
        self.face = face
        self.image_h, self.image_w, _ = image.shape
        
        self.landmarks = self._landmarks(self.face)
        # self.landmarks = self.landmarks - (x,y)
        # image = cv2.resize(image[x:x+width,y:y+height],(60,73))
        # self._process(image,self.face)

        x, y, _, _ = self.getBoundingBox()
        offset = np.array((x,y))
        # offset = offset - self.nose.getHeadTiltOffset()
        
        self.eyeLeft  = eye.Eye(image,self.landmarks,0,offset)
        self.eyeRight  = eye.Eye(image,self.landmarks,1,offset)
        

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
        
        width  = int((max_x - min_x))
        height = int((max_y - min_y))
        x = int(min_x)
        y = int(min_y) 
        return (x,y,width,height)

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
        # self.nose = nose.Nose(image,self.landmarks,self.getBoundingBox())
        
        x, y, _, _ = self.getBoundingBox()
        offset = np.array((x,y))
        # offset = offset - self.nose.getHeadTiltOffset()

        self.eyeLeft.update(image,self.landmarks,offset)
        self.eyeRight.update(image,self.landmarks,offset)

        