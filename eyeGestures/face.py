"""Module providing finding and extraction of face from image."""

import cv2
import numpy as np
import mediapipe as mp
import eyeGestures.eye as eye


class FaceFinder:

    def __init__(self, static_image_mode=True):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            static_image_mode=static_image_mode,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def find(self, image):

        assert (len(image.shape) > 2)

        try:
            face_mesh = self.mp_face_mesh.process(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            return face_mesh
        except Exception as e:
            print(f"Exception in FaceFinder: {e}")
            return None


class Face:

    def __init__(self):
        self.eyeLeft = eye.Eye(0)
        self.eyeRight = eye.Eye(1)

    def getBoundingBox(self):
        margin = 0
        min_x = np.min(self.landmarks[:, 0]) - margin
        max_x = np.max(self.landmarks[:, 0]) + margin
        min_y = np.min(self.landmarks[:, 1]) - margin
        max_y = np.max(self.landmarks[:, 1]) + margin

        width = int((max_x - min_x))
        height = int((max_y - min_y))
        x = int(min_x)
        y = int(min_y)
        return (x, y, width, height)

    def getLeftEye(self):
        return self.eyeLeft

    def getRightEye(self):
        return self.eyeRight

    def getLandmarks(self):
        return self.landmarks

    def _landmarks(self, face):

        __complex_landmark_points = face.multi_face_landmarks
        __complex_landmarks = __complex_landmark_points[0].landmark

        __face_landmarks = []
        for landmark in __complex_landmarks:
            __face_landmarks.append((
                landmark.x * self.image_w,
                landmark.y * self.image_h))

        return np.array(__face_landmarks)

    def process(self, image, face):
        try:
            self.face = face
            self.image_h, self.image_w, _ = image.shape
            self.landmarks = self._landmarks(self.face)
            # self.nose = nose.Nose(image,self.landmarks,self.getBoundingBox())

            x, y, _, _ = self.getBoundingBox()
            offset = np.array((x, y))
            # offset = offset - self.nose.getHeadTiltOffset()

            self.eyeLeft.update(image, self.landmarks, offset)
            self.eyeRight.update(image, self.landmarks, offset)
        except Exception as e:
            return None
