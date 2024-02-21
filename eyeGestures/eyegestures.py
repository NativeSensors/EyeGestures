
from eyeGestures.gazeEstimator import GazeTracker
from eyeGestures.calibration import Calibration
import eyeGestures.screenTracker.dataPoints as dp

VERSION = "1.0.0"
class EyeGestures:

    def __init__(self,
                 screen_width,
                 screen_height,
                 height,
                 width):

        self.screen_width  = screen_width
        self.screen_height = screen_height

        self.screen = dp.Screen(
                    screen_width,
                    screen_height)
        
        self.gaze = GazeTracker(screen_width,
                                screen_height,
                                width,
                                height)

        # self.calibrated = False

        # self.calibration = Calibration(self.height, self.width, 60)
        pass

    def getFeatures(self,image):
        return self.gaze.getFeatures(image)

    def getHeadDirection(self):
        return self.gaze.getHeadDirection()

    def estimate(self,image,
                context,
                calibration,
                display_width, 
                display_height,
                display_offset_x = 0,
                display_offset_y = 0,
                fixation_freeze = 0.7,
                freeze_radius=20):

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
                                freeze_radius)

    def add_offset(self,x,y):
        self.gaze.add_offset(x,y)

    # def stop_calibration(self):
    #     self.gaze.freeze_calibration()

    # def start_calibration(self):
    #     self.gaze.unfreeze_calibration()
    
    def get_contextes(self):
        return self.gaze.contextes()
    
    def rm_context(self,context):
        return self.gaze.rm_context(context)