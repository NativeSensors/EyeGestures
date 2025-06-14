"""Module providing finding and extraction of face from image."""

import cv2
import mediapipe as mp
import numpy as np

from eyeGestures.eye import Eye


class FaceFinder:  # pylint: disable=too-few-public-methods
    """Class helping finding face"""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def find(self, image):
        """Find face mesh"""

        assert len(image.shape) > 2

        try:
            face_mesh = self.mp_face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if face_mesh.multi_face_landmarks is None:
                return None

            return face_mesh
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Exception in FaceFinder: {e}")
            return None


class Face:
    """Class keeping and processing face landmarks"""

    def __init__(self):
        self.eye_left = Eye(0)
        self.eye_right = Eye(1)
        self.landmarks = None
        self.image_h = None
        self.image_w = None
        self.face = None

    def get_bounding_box(self):
        """Get bounding box of face"""
        if self.landmarks is not None:
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
        return (0, 0, 0, 0)

    def get_left_eye(self):
        """Get left eye"""
        return self.eye_left

    def get_right_eye(self):
        """Get right eye"""
        return self.eye_right

    def get_landmarks(self):
        """Get landmarks"""
        return self.landmarks

    def _landmarks(self, face):

        __complex_landmark_points = face.multi_face_landmarks
        __complex_landmarks = __complex_landmark_points[0].landmark

        __face_landmarks = []
        for landmark in __complex_landmarks:
            __face_landmarks.append((landmark.x * self.image_w, landmark.y * self.image_h))

        return np.array(__face_landmarks)

    def process(self, image, face):
        """Process face landmarks on image"""
        # try:
        self.face = face
        self.image_h, self.image_w, _ = image.shape
        self.landmarks = self._landmarks(self.face)
        # self.nose = nose.Nose(image,self.landmarks,self.getBoundingBox())

        x, y, _, _ = self.get_bounding_box()
        offset = np.array((x, y))
        # offset = offset - self.nose.getHeadTiltOffset()

        self.eye_left.update(image, self.landmarks, offset)
        self.eye_right.update(image, self.landmarks, offset)
        # except Exception as e:
        #     print(f"Caught exception: {e}")
        #     return None
