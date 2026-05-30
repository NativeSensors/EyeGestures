"""Module providing finding and extraction of face from image."""

import os
import urllib.request
from pathlib import Path
from typing import Any, NamedTuple, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np
import numpy.typing as npt
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from eyeGestures.eye import Eye

FACE_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)


def _resolve_model_asset_path(model_asset_path: Optional[str]) -> str:
    """Resolve the FaceLandmarker model path."""

    if model_asset_path:
        return model_asset_path

    env_model_path = os.getenv("EYEGESTURES_FACE_LANDMARKER_MODEL")
    if env_model_path:
        return env_model_path

    default_model_path = Path(__file__).with_name("face_landmarker_v2_with_blendshapes.task")
    if default_model_path.exists():
        return str(default_model_path)

    default_model_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(FACE_LANDMARKER_MODEL_URL, default_model_path)
    return str(default_model_path)


class FaceFinder:
    """Class helping finding face"""

    def __init__(self, model_asset_path: Optional[str] = None) -> None:
        resolved_model_path = _resolve_model_asset_path(model_asset_path)
        base_options = python.BaseOptions(model_asset_path=resolved_model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)

    def find(self, image: cv2.typing.MatLike) -> Optional[Any]:
        """Find face landmarks."""

        assert len(image.shape) > 2

        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            detection_result = self.face_landmarker.detect(mp_image)
            if not detection_result.face_landmarks:
                return None

            return detection_result
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
        face_landmarks = face.face_landmarks[0]

        scaled_landmarks = []
        for landmark in face_landmarks:
            scaled_landmarks.append((landmark.x * self.image_w, landmark.y * self.image_h))

        return np.array(scaled_landmarks)

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
