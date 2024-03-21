
from eyeGestures.gazeEstimator import GazeTracker
import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.gevent import Gevent
from eyeGestures.utils import timeit 

VERSION = "1.0.0"
class EyeGestures:

    def __init__(self,
                 screen_width,
                 screen_height,
                 height,
                 width,
                 roi_x = 225,
                 roi_y = 105,
                 roi_width = 80,
                 roi_height = 15):

        self.screen_width  = screen_width
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
        pass

    def getFeatures(self,image):
        return self.gaze.getFeatures(image)

    def getHeadDirection(self):
        return self.gaze.getHeadDirection()

    # @timeit 
    # 0.011 - 0.015 s for execution
    def estimate(self,image,
                context,
                calibration,
                display_width, 
                display_height,
                display_offset_x = 0,
                display_offset_y = 0,
                fixation_freeze = 0.7,
                freeze_radius=20,
                offset_x = 0,
                offset_y = 0):

        display = dp.Display(
            display_width,
            display_height,
            display_offset_x,
            display_offset_y
        )
    
        return self.gaze.estimate(image,
                                display,
                                context,
                                calibration,
                                fixation_freeze, 
                                freeze_radius,
                                offset_x,
                                offset_y)

    def add_offset(self,x,y):
        self.gaze.add_offset(x,y)
    
    def get_contextes(self):
        return self.gaze.contextes()
    
    def rm_context(self,context):
        return self.gaze.rm_context(context)