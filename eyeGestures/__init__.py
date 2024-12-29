from eyeGestures.face import FaceFinder, Face
from eyeGestures.Fixation import Fixation
from eyeGestures.gazeEstimator import GazeTracker
import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.calibration_v1 import Calibrator as Calibrator_v1
from eyeGestures.calibration_v2 import Calibrator as Calibrator_v2
from eyeGestures.gevent import Gevent, Cevent
from eyeGestures.utils import timeit, Buffor, low_pass_filter_fourier
import numpy as np
import pickle
import time
import cv2

VERSION = "3.0.0"

class EyeGestures_v3:
    """Main class for EyeGesture tracker. It configures and manages entire algorithm"""

    def __init__(self, calibration_radius = 1000):
        self.calibration_radius = calibration_radius 

        self.clb = dict() # Calibrator_v2()
        self.cap = None

        self.calibration = dict()

        self.average_points = dict()
        self.iterator = dict()
        self.filled_points= dict()
        self.enable_CN = False
        self.calibrate_gestures = False

        self.finder = FaceFinder()
        self.face = Face()

        # this has to be contexted
        self.prev_timestamp     = dict()
        self.prev_point         = dict()
        self.fix                = dict()
        self.velocity_max       = dict()
        self.velocity_min       = dict()
        self.fixationTracker    = dict()
        self.key_points_buffer  = dict()

        self.starting_head_position = np.zeros((1,2))
        self.starting_size = np.zeros((1,2))

    def saveModel(self, context = "main"):
        if context in self.clb:
            return pickle.dumps(self.clb[context])

    def loadModel(self,model, context = "main"):
        self.clb[context] = pickle.loads(model)

    def uploadCalibrationMap(self,points,context = "main"):
        self.addContext(context)
        self.clb[context].updMatrix(np.array(points))

    def getLandmarks(self, frame):

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,1)

        # try:
        self.face.process(
            frame,
            self.finder.find(frame)
        )

        face_landmarks = self.face.getLandmarks()
        l_eye = self.face.getLeftEye()
        r_eye = self.face.getRightEye()
        l_eye_landmarks = l_eye.getLandmarks()
        r_eye_landmarks = r_eye.getLandmarks()
        blink = l_eye.getBlink() and r_eye.getBlink()

        # get x,y offset
        x_offset = np.min(face_landmarks[:,0])
        y_offset = np.min(face_landmarks[:,1])
        x_width = np.max(face_landmarks[:,0]) - x_offset
        y_width = np.max(face_landmarks[:,1]) - y_offset

        # get head position
        head_offset = np.zeros((1,2))
        scale_x = 1
        scale_y = 1
        if np.array_equal(self.starting_head_position, np.zeros((1,2))):
            self.starting_head_position = np.array([[x_offset,y_offset]])
            self.starting_size = np.array([[x_width,y_width]])
        else:
            head_offset = np.array([[x_offset,y_offset]]) - self.starting_head_position
            scale_x = self.starting_size[0,0]/x_width
            scale_y = self.starting_size[0,1]/y_width

        # eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
        key_points = np.concatenate((l_eye_landmarks,r_eye_landmarks,np.array([[scale_x,scale_y]]),head_offset))
        key_points[:,0] = key_points[:,0] - head_offset[:,0]
        key_points[:,1] = key_points[:,1] - head_offset[:,1]

        key_points[:,0] = key_points[:,0] * scale_x
        key_points[:,1] = key_points[:,1] * scale_y

        key_points[-1,0] = head_offset[:,0]
        key_points[-1,1] = head_offset[:,1]
        # print(self.starting_size,x_width,y_width)
        subframe = frame[int(y_offset):int(y_offset+y_width),int(x_offset):int(x_offset+x_width)]
        return key_points, blink, subframe

    def whichAlgorithm(self,context="main"):
        if context in self.clb:
            return self.clb[context].whichAlgorithm()
        else:
            return "None"

    def reset(self, context = "main"):
        self.filled_points[context] = 0
        if context in self.clb:
           self.addContext(context)

    def setFixation(self,fix):
        self.fix = fix

    def addContext(self, context):
        if context not in self.clb:
            self.clb[context] = Calibrator_v2(self.calibration_radius)
            self.average_points[context] = np.zeros((20,2))
            self.filled_points[context] = 0
            self.calibration[context] = False
            self.prev_timestamp[context] = time.time()
            self.prev_point[context] = np.array((0.0,0.0))
            self.velocity_max[context] = 0
            self.velocity_min[context] = 100000000
            self.fixationTracker[context] = Fixation(0,0,100)
            self.key_points_buffer[context] = []


    def step(self, frame, calibration, width, height, context="main"):
        self.addContext(context)

        self.calibration[context] = calibration

        key_points, blink, sub_frame = self.getLandmarks(frame)
        self.key_points_buffer[context].append(key_points)
        if len(self.key_points_buffer[context]) > 10:
            self.key_points_buffer[context].pop(0)
        key_points = low_pass_filter_fourier(key_points,200)

        y_point = self.clb[context].predict(key_points)
        self.average_points[context][1:,:] = self.average_points[context][:(self.average_points[context].shape[0] - 1),:]
        self.average_points[context][0,:] = y_point

        if self.filled_points[context] < self.average_points[context].shape[0] and (y_point != np.array([0.0,0.0])).any():
            self.filled_points[context] += 1
        if self.filled_points[context] == 0:
            self.filled_points[context] = 1

        averaged_point = np.sum(self.average_points[context][:,:],axis=0)/(self.filled_points[context])

        fixation = self.fixationTracker[context].process(
            averaged_point[0], averaged_point[1])

        duration = time.time() - self.prev_timestamp[context]
        velocity = abs(averaged_point - self.prev_point[context])/duration
        velocity = np.sqrt(velocity[0]**2+velocity[1]**2)
        self.prev_point[context] = averaged_point
        self.prev_timestamp[context] = time.time()
 
        self.velocity_max[context] = max(self.velocity_max[context],velocity)
        self.velocity_min[context] = min(self.velocity_min[context],velocity)

        saccades = velocity > (self.velocity_max[context])/4

        if self.calibration[context] and (self.clb[context].insideClbRadius(averaged_point,width,height) or self.filled_points[context] < self.average_points[context].shape[0] * 10):
            self.clb[context].add(key_points,self.clb[context].getCurrentPoint(width,height))
        else: 
            self.clb[context].post_fit()

        if self.calibration[context] and self.clb[context].insideAcptcRadius(averaged_point,width,height):
            if self.clb[context].isReadyToMove():
                self.clb[context].movePoint()

        gevent = Gevent(
            point=averaged_point,
            blink=blink,
            fixation=fixation,
            saccades=saccades,
            sub_frame=sub_frame
        )
        cevent = Cevent(self.clb[context].getCurrentPoint(width,height),self.clb[context].acceptance_radius, self.clb[context].calibration_radius)
        return (gevent, cevent)

class EyeGestures_v2:
    """Main class for EyeGesture tracker. It configures and manages entire algorithm"""

    def __init__(self, calibration_radius = 1000):
        self.monitor_width  = 1
        self.monitor_height = 1
        self.calibration_radius = calibration_radius 

        self.clb = dict() # Calibrator_v2()
        self.cap = None
        self.gestures = EyeGestures_v1(285,115,200,100)

        self.calibration = dict()

        self.CN = 5

        self.average_points = dict()
        self.iterator = dict()
        self.filled_points= dict()
        self.enable_CN = False
        self.calibrate_gestures = False

        self.fix = 0.8

    def saveModel(self, context = "main"):
        if context in self.clb:
            return pickle.dumps(self.clb[context])

    def loadModel(self,model, context = "main"):
        self.clb[context] = pickle.loads(model)

    def uploadCalibrationMap(self,points,context = "main"):
        self.addContext(context)
        self.clb[context].updMatrix(np.array(points))

    def getLandmarks(self, frame, calibrate = False, context="main"):

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,1)
        # frame = cv2.resize(frame, (360, 640))

        event, cevent = self.gestures.step(
            frame,
            context,
            calibrate, # set calibration - switch to False to stop calibration
            self.monitor_width,
            self.monitor_height,
            0, 0, self.fix, 100)

        if event is not None or cevent is not None: 
            cursor_x, cursor_y = event.point[0],event.point[1]
            l_eye_landmarks = event.l_eye.getLandmarks()
            r_eye_landmarks = event.r_eye.getLandmarks()

            cursors = np.array([cursor_x,cursor_y]).reshape(1, 2)
            eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
            key_points = np.concatenate((cursors,l_eye_landmarks,r_eye_landmarks,eye_events))
            return np.array((cursor_x, cursor_y)), key_points, event.blink, event.fixation, cevent
        return np.array((0.0, 0.0)), np.array([]), 0, 0, None

    def whichAlgorithm(self,context="main"):
        if context in self.clb:
            return self.clb[context].whichAlgorithm()
        else:
            return "None"

    def setClassicImpact(self,impact):
        self.CN = impact

    def reset(self, context = "main"):
        self.filled_points[context] = 0
        if context in self.clb:
           self.addContext(context)

    def setFixation(self,fix):
        self.fix = fix

    def setClassicalImpact(self,CN):
        self.CN = CN

    def enableCNCalib(self):
        self.enable_CN = True

    def disableCNCalib(self):
        self.enable_CN = False

    def addContext(self, context):
        if context not in self.clb:
            self.clb[context] = Calibrator_v2(self.calibration_radius)
            self.average_points[context] = Buffor(20)
            self.average_points[context] = np.zeros((20,2))
            self.filled_points[context] = 0
            self.calibration[context] = False


    def step(self, frame, calibration, width, height, context="main"):
        self.addContext(context)

        self.calibration[context] = calibration
        self.monitor_width = width
        self.monitor_height = height

        classic_point, key_points, blink, fixation, cevent = self.getLandmarks(frame,
                                                                               self.calibrate_gestures and self.enable_CN,
                                                                               context = context)

        if cevent is None:
            return (None, None)

        margin = 10
        if (classic_point[0] <= margin) and self.calibration[context]:
            self.calibrate_gestures = cevent.calibration
        elif (classic_point[0] >= width - margin) and self.calibration[context]:
            self.calibrate_gestures = cevent.calibration
        elif (cevent.point[1] <= margin) and self.calibration[context]:
            self.calibrate_gestures = cevent.calibration
        elif (classic_point[1] >= height - margin) and self.calibration[context]:
            self.calibrate_gestures = cevent.calibration
        else:
            self.calibrate_gestures = False

        y_point = self.clb[context].predict(key_points)
        self.average_points[context][1:,:] = self.average_points[context][:(self.average_points[context].shape[0] - 1),:]
        if fixation <= self.fix:
            self.average_points[context][0,:] = y_point

        if self.filled_points[context] < self.average_points[context].shape[0] and (y_point != np.array([0.0,0.0])).any():
            self.filled_points[context] += 1
        averaged_point = (np.sum(self.average_points[context][:,:],axis=0) + (classic_point * self.CN))/(self.filled_points[context] + self.CN)
        
        if self.calibration[context] and (self.clb[context].insideClbRadius(averaged_point,width,height) or self.filled_points[context] < self.average_points[context].shape[0] * 10):
            self.clb[context].add(key_points,self.clb[context].getCurrentPoint(width,height))
        else: 
            self.clb[context].post_fit()

        if self.calibration[context] and self.clb[context].insideAcptcRadius(averaged_point,width,height):
            if self.clb[context].isReadyToMove():
                self.clb[context].movePoint()
        

        gevent = Gevent(averaged_point,blink,fixation)
        cevent = Cevent(self.clb[context].getCurrentPoint(width,height),self.clb[context].acceptance_radius, self.clb[context].calibration_radius)
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
        cevent = None

        if event is not None:
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