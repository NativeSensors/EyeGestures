
import numpy as np
from eyeGestures.nose import NoseDirection
from eyeGestures.face import FaceFinder, Face
from eyeGestures.calibration   import GazePredictor, CalibrationData
from eyeGestures.processing    import EyeProcessor
from eyeGestures.screenTracker import ScreenManager
from eyeGestures.contexter     import Contexter 

def isInside(circle_x, circle_y, r, x, y):
     
    # Compare radius of circle
    # with distance of its center
    # from given point
    if ((x - circle_x) * (x - circle_x) +
        (y - circle_y) * (y - circle_y) <= r * r):
        return True
    else:
        return False
 
class Gevent:

    def __init__(self,
                 point,
                 point_screen,
                 blink,
                 fixation,
                 l_eye,
                 r_eye,
                 screen_man,
                 context):

        self.point = point
        self.blink = blink
        self.fixation = fixation
        self.point_screen = point_screen
        
        ## ALL DEBUG DATA
        self.l_eye = l_eye
        self.r_eye = r_eye
        self.screen_man = screen_man
        self.context = context

class Fixation:

    def __init__(self,x,y,radius = 100):
        self.radius = radius
        self.fixation = 0.0
        self.x = x 
        self.y = y
        pass

    def process(self,x,y):
        
        if (x - self.x)**2 + (y - self.y)**2 < self.radius**2:
            self.fixation = min(self.fixation + 0.02, 1.0)
        else:
            self.x = x
            self.y = y
            self.fixation = 0

        return self.fixation
class GazeTracker:

    N_FEATURES = 16

    def __init__(self,screen_width,screen_heigth,
                 eye_screen_w,eye_screen_h,
                 monitor_offset_x = 0,
                 monitor_offset_y = 0):

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h

        self.eyeProcessorLeft  = EyeProcessor(eye_screen_w,eye_screen_h)
        self.eyeProcessorRight = EyeProcessor(eye_screen_w,eye_screen_h)

        self.screen_man = ScreenManager(screen_width,
                                        screen_heigth,
                                        self.eye_screen_w,
                                        self.eye_screen_h,
                                        monitor_offset_x,
                                        monitor_offset_y)

        self.noseDirection = NoseDirection()
        self.predictor = GazePredictor()
        self.finder = FaceFinder()

        self.gazeFixation = Fixation(0,0,100)

        self.calibrationData = CalibrationData()

        self.buffor = []
        self.bufforLength = 10

        # those are used for analysis
        self.__headDir = [0.5,0.5]

        self.point_screen = [0.0,0.0]
        self.freezed_point = [0.0,0.0]

        self.contexter = Contexter()
        self.face = Face()

    def freeze_calibration(self):
        pass
        # self.screen_man.freeze_calibration()

    def unfreeze_calibration(self):
        pass
        # self.screen_man.unfreeze_calibration()

    def __gaze_intersection(self,l_eye,r_eye):
        l_pupil = l_eye.getPupil()
        l_gaze  = l_eye.getGaze()
        
        r_pupil = r_eye.getPupil()        
        r_gaze  = r_eye.getGaze()

        l_end = l_gaze + l_pupil
        r_end = r_gaze + r_pupil

        l_m = (l_end[1] - l_pupil[1])/(l_end[0] - l_pupil[0])
        r_m = (r_end[1] - r_pupil[1])/(r_end[0] - r_pupil[0])

        l_b = l_end[1] - l_m * l_end[0]
        r_b = r_end[1] - r_m * r_end[0]

        i_x = (r_b - l_b)/(l_m - r_m)
        i_y = r_m * i_x + r_b
        return (i_x,i_y)

    def estimate(self,image,context_id,fixation_freeze = 0.7, freeze_radius=20):

        event = None
        face_mesh = self.getFeatures(image)
    
        self.face.process(image,face_mesh)
        if not self.face is None:
            
            l_eye = self.face.getLeftEye()
            r_eye = self.face.getRightEye()
            l_pupil = l_eye.getPupil()
            r_pupil = r_eye.getPupil()
            
            intersection_x,_ = self.__gaze_intersection(l_eye,r_eye)
            # TODO: check what happens here before with l_pupil
            self.eyeProcessorLeft.append( l_pupil, l_eye.getLandmarks())
            self.eyeProcessorRight.append(r_pupil, r_eye.getLandmarks())

            # This scales pupil move to the screen we observe
            l_point = self.eyeProcessorLeft.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            l_point = np.array((int(intersection_x),l_point[1]))
            r_point = self.eyeProcessorRight.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            r_point = np.array((int(intersection_x),r_point[1]))

            compound_point = np.array(((l_point + r_point)/2),dtype=np.uint32)

            # self.point_screen = self.screen_man.process(compound_point)
            fixation = self.gazeFixation.process(self.point_screen[0],self.point_screen[1])        
            
            blink = l_eye.getBlink() or r_eye.getBlink()
            if blink == True and fixation < fixation_freeze:
                return None
            
            blink = blink and (fixation > fixation_freeze)
            
            if fixation > fixation_freeze:
                r = freeze_radius
                if not isInside(self.freezed_point[0],self.freezed_point[1],r,self.point_screen[0],self.point_screen[1]):
                    self.freezed_point = self.point_screen

                event = Gevent(compound_point,
                        self.freezed_point,
                        blink,
                        fixation,
                        l_eye,
                        r_eye,
                        self.screen_man,
                        context_id)
            else:
                self.freezed_point = self.point_screen
                event = Gevent(compound_point,
                            self.point_screen,
                            blink,
                            fixation,
                            l_eye,
                            r_eye,
                            self.screen_man,
                            context_id)

        return event
    
    def get_contextes(self):
        return self.finder.get_contextes()

    def add_offset(self,x,y):
        self.screen_man.push_window(x,y)

    def getCalibration(self):
        return self.calibrationData.get()

    def getFeatures(self,image):
        face_mesh = self.finder.find(image)
        return face_mesh
        
    def getHeadDirection(self):
        return self.__headDir        