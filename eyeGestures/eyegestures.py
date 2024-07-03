
from eyeGestures.gazeEstimator import GazeTracker
import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.calibration_v1 import Calibrator as Calibrator_v1
from eyeGestures.calibration_v2 import Calibrator as Calibrator_v2, CalibrationMatrix, euclidean_distance
from eyeGestures.gevent import Gevent, Cevent
from eyeGestures.utils import timeit
import numpy as np
import pickle
import cv2

import random

VERSION = "2.0.0"

class EyeGestures_v2:
    """Main class for EyeGesture tracker. It configures and manages entire algorithm"""


    PRECISION_LIMIT = 50
    PRECISION_STEP = 10
    ACCEPTANCE_RADIUS = 500
    CALIBRATION_RADIUS = 1000
    EYEGESTURES_CALIBRATION_THRESH = 850
    EYEGESTURES_CALIBRATION_FILENAME = 'eygestures_calib.eyec'

    def __init__(self):
        self.monitor_width  = 1
        self.monitor_height = 1

        self.clb = Calibrator_v2()
        self.cap = None
        self.gestures = EyeGestures_v1(285,115,200,100)

        self.calibration = False

        self.CN = 5

        self.trackerSignal = None
        self.fitSignal = None

        self.average_points = np.zeros((20,2))
        self.filled_points = 0
        self.enable_CN = False
        self.calibrate_gestures = False
        self.calibrationMat = CalibrationMatrix()
        self.fit_point = self.calibrationMat.getNextPoint()

        self.iterator = 0
        self.fix = 0.8

        self.precision_limit = self.PRECISION_LIMIT
        self.precision_step = self.PRECISION_STEP
        self.acceptance_radius = self.ACCEPTANCE_RADIUS
        self.calibration_radius = self.CALIBRATION_RADIUS
        # after corssing this thresh we are disabling classical calib
        self.eyegestures_calibration_threshold = self.EYEGESTURES_CALIBRATION_THRESH

    def saveModel(self):
        return pickle.dumps(self.clb)

    def loadModel(self,model):
        self.clb = pickle.loads(model)

    def uploadCalibrationMap(self,points):
        self.calibrationMat.update_calibration_matrix(np.array(points))
        self.fit_point = self.calibrationMat.getNextPoint()

    def getLandmarks(self, frame, calibrate = False):

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,1)
        # frame = cv2.resize(frame, (360, 640))

        event, cevent = self.gestures.step(
            frame,
            "main",
            calibrate, # set calibration - switch to False to stop calibration
            self.monitor_width,
            self.monitor_height,
            0, 0, self.fix, 100)

        cursor_x, cursor_y = event.point[0],event.point[1]
        l_eye_landmarks = event.l_eye.getLandmarks()
        r_eye_landmarks = event.r_eye.getLandmarks()

        cursors = np.array([cursor_x,cursor_y]).reshape(1, 2)
        eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
        key_points = np.concatenate((cursors,l_eye_landmarks,r_eye_landmarks,eye_events))
        return  np.array((cursor_x, cursor_y)), key_points, event.blink, event.fixation, cevent

    def increase_precision(self):
        if self.acceptance_radius > self.precision_limit:
            self.acceptance_radius -= self.precision_step
        if self.calibration_radius > self.precision_limit and self.acceptance_radius < self.calibration_radius:
            self.calibration_radius -= self.precision_step

    def setClassicImpact(self,impact):
        self.CN = impact

    def reset(self):
        self.acceptance_radius = self.ACCEPTANCE_RADIUS
        self.calibration_radius = self.CALIBRATION_RADIUS
        self.average_points = np.zeros((20,2))
        self.filled_points = 0
        self.clb.unfit()

    def setFixation(self,fix):
        self.fix = fix

    def setClassicalImpact(self,CN):
        self.CN = CN

    def enableCNCalib(self):
        self.enable_CN = True

    def disableCNCalib(self):
        self.enable_CN = False

    def step(self, frame, calibration, width, height):
        self.calibration = calibration
        self.monitor_width = width
        self.monitor_height = height

        classic_point, key_points, blink, fixation, cevent = self.getLandmarks(frame,self.calibrate_gestures and self.enable_CN)

        margin = 10
        if (classic_point[0] <= margin) and self.calibration:
            self.calibrate_gestures = cevent.calibration
        elif (classic_point[0] >= width - margin) and self.calibration:
            self.calibrate_gestures = cevent.calibration
        elif (cevent.point[1] <= margin) and self.calibration:
            self.calibrate_gestures = cevent.calibration
        elif (classic_point[1] >= height - margin) and self.calibration:
            self.calibrate_gestures = cevent.calibration
        else:
            self.calibrate_gestures = False

        y_point = self.clb.predict(key_points)
        self.average_points[1:,:] = self.average_points[:(self.average_points.shape[0] - 1),:]
        if fixation <= self.fix:
            self.average_points[0,:] = y_point

        if self.filled_points < self.average_points.shape[0] and (y_point != np.array([0.0,0.0])).any():
            self.filled_points += 1

        averaged_point = (np.sum(self.average_points[:,:],axis=0) + (classic_point * self.CN))/(self.filled_points + self.CN)

        if self.calibration and (euclidean_distance(averaged_point,self.fit_point) < self.calibration_radius or self.filled_points < self.average_points.shape[0] * 10):
            self.clb.add(key_points,self.fit_point)

        if self.calibration and (euclidean_distance(averaged_point,self.fit_point) < self.acceptance_radius):
            self.iterator += 1
            if self.iterator > 10:
                self.iterator = 0
                self.fit_point = self.calibrationMat.getNextPoint(width,height)
                self.increase_precision()

        gevent = Gevent(averaged_point,blink,fixation >= self.fix)
        cevent = Cevent(self.fit_point,self.acceptance_radius, self.calibration_radius)
        return (gevent, cevent)

class EyeGestures_v1:
    """Main class for EyeGesture tracker. It configures and manages entier algorithm"""

    def __init__(self,
                 roi_x=225,
                 roi_y=105,
                 roi_width=80,
                 roi_height=15):

        screen_width = 500
        screen_height = 500
        height = 250
        width = 250

        roi_x = roi_x % screen_width
        roi_y = roi_y % screen_height
        roi_width = roi_width % screen_width
        roi_height = roi_height % screen_height

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.screen = dp.Screen(
            screen_width,
            screen_height)

        self.gaze = GazeTracker(screen_width,
                                screen_height,
                                width,
                                height,
                                roi_x,
                                roi_y,
                                roi_width,
                                roi_height)

        self.calibrators = dict()
        self.calibrate = False

    def getFeatures(self, image):
        """[NOT RECOMMENDED] Function allowing for extraction of gaze features from image"""

        return self.gaze.getFeatures(image)

    # @timeit
    # 0.011 - 0.015 s for execution
    def step(self, image,
                 context,
                 calibration,
                 display_width,
                 display_height,
                 display_offset_x=0,
                 display_offset_y=0,
                 fixation_freeze=0.7,
                 freeze_radius=20,
                 offset_x=0,
                 offset_y=0):
        """Function performing estimation and returning event object"""

        display = dp.Display(
            display_width,
            display_height,
            display_offset_x,
            display_offset_y
        )

        # allow for random recalibration shot
        event = self.gaze.estimate(image,
                                  display,
                                  context,
                                  calibration,
                                  fixation_freeze,
                                  freeze_radius,
                                  offset_x,
                                  offset_y)

        cursor_x,cursor_y = event.point[0],event.point[1]
        if context in self.calibrators:
            self.calibrate = self.calibrators[context].calibrate(cursor_x,cursor_y,event.fixation)
        else:
            self.calibrators[context] = Calibrator_v1(display_width,display_height,cursor_x,cursor_y)
            self.calibrate = self.calibrators[context].calibrate(cursor_x,cursor_y,event.fixation)

        cpoint = self.calibrators[context].get_current_point()
        calibration = self.calibrate and cpoint != (0,0)
        cevent = Cevent(cpoint,100, 100, calibration)

        return (event, cevent)