import pickle
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import numpy.typing as npt

from eyeGestures.face import Face, FaceFinder
from eyeGestures.Fixation import Fixation
from eyeGestures.utils import recoverable

try:
    from EyegesturesEngine import EyeGesturesEnginePython as RustEyeGesturesEngine
except ImportError:
    RustEyeGesturesEngine = None

VERSION = "4.0.0"

class EyeGestures_v4:
    """Main class for EyeGesture tracker. It configures and manages entire algorithm"""

    def __init__(self, calibration_radius: int = 1000) -> None:
        self.calibration_radius = calibration_radius

        self.average_points: npt.NDArray[np.float64] = np.zeros((1, 2))
        self.calibration: bool = False
        self.filled_points: int = 0

        self.finder = FaceFinder()
        self.face = Face()
        self.engine = None

        self.fix: Optional[float] = None
        self.fixationTracker: Dict[str, Fixation] = dict()
        self.key_points_buffer: Dict[str, List[npt.NDArray[np.float64]]] = dict()

        self.starting_head_position = np.zeros((1, 2))
        self.starting_size = np.zeros((1, 2))
        
    def uploadCalibrationMap(self, points: npt.NDArray[np.float64], context: str = "main") -> None:
        self.clb.updMatrix(np.array(points))

    def getLandmarks(self, frame: cv2.typing.MatLike) -> Tuple[npt.NDArray[np.float64], bool, cv2.typing.MatLike]:

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        # try:
        self.face.process(frame, self.finder.find(frame))
        face_landmarks = self.face.get_landmarks()
        assert face_landmarks is not None
        l_eye = self.face.get_left_eye()
        r_eye = self.face.get_right_eye()
        l_eye_landmarks = l_eye.getLandmarks()
        r_eye_landmarks = r_eye.getLandmarks()
        blink = l_eye.getBlink() and r_eye.getBlink()

        # get x,y offset
        x_offset = np.min(face_landmarks[:, 0])
        y_offset = np.min(face_landmarks[:, 1])
        x_width = np.max(face_landmarks[:, 0]) - x_offset
        y_width = np.max(face_landmarks[:, 1]) - y_offset

        # get head position
        head_offset = np.zeros((1, 2))
        scale_x = 1
        scale_y = 1
        if np.array_equal(self.starting_head_position, np.zeros((1, 2))):
            self.starting_head_position = np.array([[x_offset, y_offset]])
            self.starting_size = np.array([[x_width, y_width]])
        else:
            head_offset = np.array([[x_offset, y_offset]]) - self.starting_head_position
            scale_x = self.starting_size[0, 0] / x_width
            scale_y = self.starting_size[0, 1] / y_width

        # eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
        assert l_eye_landmarks is not None
        assert r_eye_landmarks is not None
        key_points: npt.NDArray[np.float64] = np.concatenate(
            (
                l_eye_landmarks,
                r_eye_landmarks,
                np.array([[scale_x, scale_y]]),
                head_offset,
            )
        )
        key_points[:, 0] = key_points[:, 0] - head_offset[:, 0]
        key_points[:, 1] = key_points[:, 1] - head_offset[:, 1]

        key_points[:, 0] = key_points[:, 0] * scale_x
        key_points[:, 1] = key_points[:, 1] * scale_y

        key_points[-1, 0] = head_offset[0, 0]
        key_points[-1, 1] = head_offset[0, 1]
        # print(self.starting_size,x_width,y_width)
        subframe = frame[
            int(y_offset) : int(y_offset + y_width),
            int(x_offset) : int(x_offset + x_width),
        ]
        return key_points, blink, subframe

    def whichAlgorithm(self, context: str = "main") -> str:
        return "rust engine"

    def reset(self, context: str = "main") -> None:
        self.filled_points = 0

    def setFixation(self, fix: float) -> None:
        self.fix = fix


    @recoverable(ret_error_params=(None, None, None))
    def step(
        self, frame: cv2.typing.MatLike, width: int, height: int,):

        if self.engine is None:
            self.engine = RustEyeGesturesEngine(width, height)

        landmarks = self.finder.find(frame).face_landmarks[0]
        scaled_landmarks = []
        for landmark in landmarks:
            scaled_landmarks.append((landmark.x, landmark.y))
        scaled_landmarks = np.array(scaled_landmarks)
        result = self.engine.process(scaled_landmarks.flatten().tolist())

        x, y          = result[0], result[1]
        is_calibrating = result[2] == 1.0
        calib_x, calib_y = result[3], result[4]
        calib_x = min(max(calib_x, 0), width) 
        calib_y = min(max(calib_y, 0), height)
        return [x, y], is_calibrating, [calib_x, calib_y]
