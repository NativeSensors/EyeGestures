
from eyeGestures.gazeestimator import GazeTracker
from eyeGestures.calibration import Calibration


class EyeGestures:

    def __init__(self,screen_width,screen_height,
                 height,width,
                 monitor_offset_x = 0,
                 monitor_offset_y = 0):

        self.width  = width
        self.height = height

        self.gaze = GazeTracker(screen_width,
                                screen_height,
                                width,height,
                                monitor_offset_x,
                                monitor_offset_y)

        self.calibrated = False

        self.calibration = Calibration(self.height, self.width, 60)
        pass

    def __onCalibrated(self):
        self.gaze.fit()
        self.calibrated = True

    def calibrate(self,image):
        if(not self.calibrated and not self.calibration.inProgress()):
            self.calibration.start(self.__onCalibrated)

        point = self.calibration.getTrainingPoint()
        self.gaze.calibrate(point,image)
        
        if len(self.gaze.getCalibration()[0]) > 10:
            self.gaze.fit()
            self.calibrated = True

        return point 

    def getFeatures(self,image):
        return self.gaze.getFeatures(image)

    def getHeadDirection(self):
        return self.gaze.getHeadDirection()

    def isCalibrated(self):
        return self.calibrated and not self.calibration.inProgress()

    def estimate(self,image ,fixation_freeze = 0.7):
        return self.gaze.estimate(image,fixation_freeze)

    def stop_calibration(self):
        self.gaze.freeze_calibration()

    def start_calibration(self):
        self.gaze.unfreeze_calibration()