
import numpy as np
from eyeGestures.nose import NoseDirection
from eyeGestures.face import FaceFinder, Face
from eyeGestures.processing    import EyeProcessor
from eyeGestures.gazeContexter import GazeContext 
from eyeGestures.screenTracker.screenTracker import ScreenManager
import eyeGestures.screenTracker.dataPoints as dp

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

        self.screen = dp.Screen(screen_width,screen_heigth)

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h

        self.eyeProcessorLeft  = EyeProcessor(eye_screen_w,eye_screen_h)
        self.eyeProcessorRight = EyeProcessor(eye_screen_w,eye_screen_h)

        self.screen_man = ScreenManager()

        self.finder = FaceFinder()

        self.gazeFixation = Fixation(0,0,100)

        # those are used for analysis
        self.__headDir = [0.5,0.5]

        self.point_screen = [0.0,0.0]
        self.freezed_point = [0.0,0.0]

        self.face = Face()
        self.GContext = GazeContext()
    #     self.calibration = False

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
    
    def __pupil(self, eye, eyeProcessor, intersection_x, buffor):
        eyeProcessor.loadBuffor(buffor)

        eyeProcessor.append( eye.getPupil(), eye.getLandmarks())
        point = eyeProcessor.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
        point = np.array((int(intersection_x),point[1]))
        
        return point,eyeProcessor.dumpBuffor()
    
    def estimate(self,
                 image,
                 display,
                 context_id,
                 calibration,
                 fixation_freeze = 0.7, 
                 freeze_radius=20):

        event = None
        face_mesh = self.getFeatures(image)
        self.face.process(image, face_mesh)

        context = self.GContext.get(context_id,display)
        context.calibration = calibration
        
        if not self.face is None:
            
            l_eye   = self.face.getLeftEye()
            r_eye   = self.face.getRightEye()
            
            # TODO: check what happens here before with l_pupil
            intersection_x,_ = self.__gaze_intersection(l_eye,r_eye)
            l_point, l_buffor = self.__pupil(l_eye,self.eyeProcessorLeft,  intersection_x, context.l_pupil)
            r_point, r_buffor = self.__pupil(r_eye,self.eyeProcessorRight, intersection_x, context.r_pupil)
            
            context.l_pupil = l_buffor
            context.r_pupil = r_buffor

            compound_point = np.array(((l_point + r_point)/2),dtype=np.uint32)

            context.gazeBuffor.add(compound_point)

            self.point_screen, roi, cluster = self.screen_man.process(context.gazeBuffor,
                                                        context.roi,
                                                        context.edges,
                                                        self.screen,
                                                        context.display,
                                                        context.calibration
                                                        )
            
            context.roi = roi
            x,y,width,height = cluster.getBoundaries()
            context.cluster_boundaries.x = x
            context.cluster_boundaries.y = y
            context.cluster_boundaries.width = width
            context.cluster_boundaries.height = height
            self.GContext.update(context_id,context)

            ###########################################################
            
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
                        context,
                        context_id)
            else:
                self.freezed_point = self.point_screen
                event = Gevent(compound_point,
                            self.point_screen,
                            blink,
                            fixation,
                            l_eye,
                            r_eye,
                            context,
                            context_id)

        return event
    
    def get_contextes(self):
        return self.finder.get_contextes()

    def add_offset(self,x,y):
        self.screen_man.push_window(x,y)

    def getFeatures(self,image):
        face_mesh = self.finder.find(image)
        return face_mesh
        
    def getHeadDirection(self):
        return self.__headDir        