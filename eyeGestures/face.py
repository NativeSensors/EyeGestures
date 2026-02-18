"""Module providing finding and extraction of face from image."""

from typing import Any, NamedTuple, Optional, Tuple

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat

import numpy as np
import numpy.typing as npt

from eyeGestures.eye import Eye


class FaceFinder:
    """Class helping finding face"""

    def __init__(self) -> None:
        BaseOptions = python.BaseOptions
        FaceLandmarker = vision.FaceLandmarker
        FaceLandmarkerOptions = vision.FaceLandmarkerOptions
        VisionRunningMode = vision.RunningMode
        options = FaceLandmarkerOptions(
            base_options = BaseOptions(
                model_asset_path = r"C:\Users\vvams\PycharmProjects\EyeGestures\eyeGestures\task_model\face_landmarker.task"
            ),
            running_mode = VisionRunningMode.IMAGE,
            num_faces = 1,
            min_face_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_face_mesh = FaceLandmarker.create_from_options(options)

    def find(self, image: cv2.typing.MatLike) -> Optional[Any]:
        """Find face mesh"""

        assert len(image.shape) > 2

        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format = ImageFormat.SRGB, data = image_rgb)
            face_mesh = self.mp_face_mesh.detect(mp_image)
            if face_mesh.face_landmarks is None:
                return None

            return face_mesh
        except Exception as e:
            print(f"Exception in FaceFinder: {e}")
            return None


class Face:
    """Class keeping and processing face landmarks"""

    def __init__(self) -> None:
        self.eye_left = Eye(0)
        self.eye_right = Eye(1)
        self.landmarks: Optional[npt.NDArray[np.float64]] = None
        self.image_h: Optional[int] = None
        self.image_w: Optional[int] = None
        self.face: Optional[NamedTuple] = None

    def get_bounding_box(self) -> Tuple[int, int, int, int]:
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

    def get_left_eye(self) -> Eye:
        """Get left eye"""
        return self.eye_left

    def get_right_eye(self) -> Eye:
        """Get right eye"""
        return self.eye_right

    def get_landmarks(self) -> Optional[npt.NDArray[np.float64]]:
        """Get landmarks"""
        return self.landmarks

    def _landmarks(self, face: Any) -> npt.NDArray[np.float64]:

        __complex_landmark_points = face.face_landmarks[0]

        __face_landmarks = []
        for landmark in __complex_landmark_points:
            __face_landmarks.append((landmark.x * self.image_w, landmark.y * self.image_h))

        return np.array(__face_landmarks)

    def process(self, image: cv2.typing.MatLike, face: Optional[Any]) -> None:
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
