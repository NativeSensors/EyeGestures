"""Module providing a Gaze Events."""

from typing import Any, Optional

import cv2
import numpy as np
import numpy.typing as npt

from eyeGestures.eye import Eye


class Gevent:
    """Class representing gaze event, with tracked points scaled to screen, blink and fixation."""

    def __init__(
        self,
        point: npt.NDArray[np.float64],
        blink: bool,
        fixation: float,
        l_eye: Optional[Eye] = None,
        r_eye: Optional[Eye] = None,
        screen_man: Optional[Any] = None,
        roi: Optional[Any] = None,
        edges: Optional[Any] = None,
        cluster: Optional[Any] = None,
        context: Optional[Any] = None,
        saccades: bool = False,
        sub_frame: Optional[cv2.typing.MatLike] = None,
    ):

        self.point = point
        self.blink = blink
        self.fixation = fixation
        self.saccades = saccades

        # ALL DEBUG DATA
        self.roi = roi
        self.edges = edges
        self.l_eye = l_eye
        self.r_eye = r_eye
        self.cluster = cluster
        self.context = context
        self.screen_man = screen_man
        self.sub_frame = sub_frame


class Cevent:
    """Class representing gaze event, with tracked points scaled to screen, blink and fixation."""

    def __init__(
        self, point: npt.NDArray[np.float64], acceptance_radius: int, calibration_radius: int, calibration: bool = False
    ) -> None:

        self.point = point
        self.acceptance_radius = acceptance_radius
        self.calibration_radius = calibration_radius
        self.calibration = calibration
