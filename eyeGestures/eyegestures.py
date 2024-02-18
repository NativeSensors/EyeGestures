
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

    def getFeatures(self,image):
        return self.gaze.getFeatures(image)

    def getHeadDirection(self):
        return self.gaze.getHeadDirection()

    def isCalibrated(self):
        return self.calibrated and not self.calibration.inProgress()

    def estimate(self,image, context, fixation_freeze = 0.7, freeze_radius=20):
        return self.gaze.estimate(image, context, fixation_freeze, freeze_radius)

    def add_offset(self,x,y):
        self.gaze.add_offset(x,y)

    def stop_calibration(self):
        self.gaze.freeze_calibration()

    def start_calibration(self):
        self.gaze.unfreeze_calibration()
    
    def get_contextes(self):
        return self.gaze.contextes()