import os
import sys
import cv2
import unittest
import numpy as np
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

class TestBasic(unittest.TestCase):


    def test_basic_run(self):
        gestures = EyeGestures_v3()
        # Load image (color)
        frame = cv2.imread("tests/data/face_2.jpg")
        calibrate = True
        screen_width = 100
        screen_height = 100

        x = np.arange(0, 1.1, 0.2)
        y = np.arange(0, 1.1, 0.2)

        xx, yy = np.meshgrid(x, y)
        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        gestures.uploadCalibrationMap(calibration_map)

        event, calibration = gestures.step(frame, calibrate, screen_width, screen_height)

        self.assertNotEqual(event, None)
        self.assertNotEqual(calibration, None)

    def test_basic_run_calibration_finished(self):
        gestures = EyeGestures_v3()
        # Load image (color)
        frame = cv2.imread("tests/data/face_2.jpg")

        calibrate = True
        screen_width = 100
        screen_height = 100

        x = np.arange(0, 1.1, 1.0)
        y = np.arange(0, 1.1, 1.0)

        xx, yy = np.meshgrid(x, y)
        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        gestures.uploadCalibrationMap(calibration_map)

        for _ in range(500):
            event, calibration = gestures.step(frame, calibrate, screen_width, screen_height)

        calibrate = False
        event, calibration = gestures.step(frame, calibrate, screen_width, screen_height)

        self.assertNotEqual(event, None)
        self.assertNotEqual(calibration, None)

    def test_upload_calibration_mask(self):
        gestures = EyeGestures_v3()

        x = np.arange(0, 1.1, 0.2)
        y = np.arange(0, 1.1, 0.2)

        xx, yy = np.meshgrid(x, y)
        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        gestures.uploadCalibrationMap(calibration_map)
