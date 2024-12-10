
from eyeGestures.face import FaceFinder, Face
from eyeGestures.Fixation import Fixation
from eyeGestures.calibration_v2 import Calibrator as Calibrator_v2
from eyeGestures.gevent import Gevent, Cevent
from eyeGestures.utils import Buffor
import numpy as np
import pickle
import time
import cv2

class EyeGestures_v3:
    """Main class for EyeGesture tracker. It configures and manages entire algorithm"""

    def __init__(self, calibration_radius = 1000):
        self.monitor_width  = 1
        self.monitor_height = 1
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
        # frame = cv2.resize(frame, (360, 640))

        try:
            # decoupling from V1
            self.face.process(
                frame,
                self.finder.find(frame)
            )
            l_eye = self.face.getLeftEye()
            r_eye = self.face.getRightEye()
            l_eye_landmarks = l_eye.getLandmarks()
            r_eye_landmarks = r_eye.getLandmarks()
            blink = l_eye.getBlink() and r_eye.getBlink()
            
            # eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
            key_points = np.concatenate((l_eye_landmarks,r_eye_landmarks))
            return key_points, blink
        except:
            pass
        return np.array([]), 0

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
            self.average_points[context] = Buffor(5)
            self.iterator[context] = 0
            self.average_points[context] = np.zeros((20,2))
            self.filled_points[context] = 0
            self.calibration[context] = False
            self.prev_timestamp[context] = time.time()
            self.prev_point[context] = np.array((0.0,0.0))
            self.fix[context] = 0.8
            self.velocity_max[context] = 0
            self.velocity_min[context] = 100000000
            self.fixationTracker[context] = Fixation(0,0,100)


    def step(self, frame, calibration, width, height, context="main"):
        self.addContext(context)

        self.calibration[context] = calibration
        self.monitor_width = width
        self.monitor_height = height

        key_points, blink = self.getLandmarks(frame)


        y_point = self.clb[context].predict(key_points)
        self.average_points[context][1:,:] = self.average_points[context][:(self.average_points[context].shape[0] - 1),:]
        self.average_points[context][0,:] = y_point

        if self.filled_points[context] < self.average_points[context].shape[0] and (y_point != np.array([0.0,0.0])).any():
            self.filled_points[context] += 1
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

        saccades = velocity > (self.velocity_max[context]+self.velocity_min[context])/4

        if self.calibration[context] and (self.clb[context].insideClbRadius(averaged_point,width,height) or self.filled_points[context] < self.average_points[context].shape[0] * 10):
            self.clb[context].add(key_points,self.clb[context].getCurrentPoint(width,height))
        else: 
            self.clb[context].post_fit()

        if self.calibration[context] and self.clb[context].insideAcptcRadius(averaged_point,width,height):
            self.iterator[context] += 1
            if self.iterator[context] > 10:
                self.iterator[context] = 0
                self.clb[context].movePoint()

        gevent = Gevent(
            point=averaged_point,
            blink=blink,
            fixation=fixation,
            saccades=saccades
        )
        cevent = Cevent(self.clb[context].getCurrentPoint(width,height),self.clb[context].acceptance_radius, self.clb[context].calibration_radius)
        return (gevent, cevent)
