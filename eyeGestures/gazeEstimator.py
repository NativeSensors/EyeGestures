
import numpy as np
from eyeGestures.gevent import Gevent
from eyeGestures.face import FaceFinder, Face
from eyeGestures.Fixation import Fixation
from eyeGestures.processing import EyeProcessor
from eyeGestures.gazeContexter import GazeContext
from eyeGestures.screenTracker.screenTracker import ScreenManager
import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.utils import Buffor


def isInside(circle_x, circle_y, r, x, y):
    """Function checking if points are inside the circle"""

    # Compare radius of circle
    # with distance of its center
    # from given point
    if ((x - circle_x) * (x - circle_x) +
            (y - circle_y) * (y - circle_y) <= r * r):
        return True
    else:
        return False


class GazeTracker:
    """Class processing images and returning gaze tracker"""

    N_FEATURES = 16

    def __init__(self, screen_width, screen_heigth,
                 eye_screen_w, eye_screen_h,
                 roi_x, roi_y,
                 roi_width, roi_height,
                 monitor_offset_x=0,
                 monitor_offset_y=0):

        self.screen = dp.Screen(screen_width, screen_heigth)

        self.offset_x = 0
        self.offset_y = 0

        self.roi_x = roi_x
        self.roi_y = roi_y
        self.roi_width = roi_width
        self.roi_height = roi_height

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h

        self.eyeProcessorLeft = EyeProcessor(eye_screen_w, eye_screen_h)
        self.eyeProcessorRight = EyeProcessor(eye_screen_w, eye_screen_h)

        self.screen_man = ScreenManager()

        self.finder = FaceFinder()

        # those are used for analysis
        self.__headDir = [0.5, 0.5]

        self.point_screen = [0.0, 0.0]
        self.freezed_point = [0.0, 0.0]

        self.face = Face()
        self.GContext = GazeContext()
    #     self.calibration = False

    def __gaze_intersection(self, l_eye, r_eye, l_buff, r_buff):
        l_pupil = l_eye.getPupil()
        l_gaze = l_eye.getGaze(l_buff)

        r_pupil = r_eye.getPupil()
        r_gaze = r_eye.getGaze(r_buff)

        l_end = l_gaze + l_pupil
        r_end = r_gaze + r_pupil

        l_m = (l_end[1] - l_pupil[1])/(l_end[0] - l_pupil[0])
        r_m = (r_end[1] - r_pupil[1])/(r_end[0] - r_pupil[0])

        l_b = l_end[1] - l_m * l_end[0]
        r_b = r_end[1] - r_m * r_end[0]

        i_x = (r_b - l_b)/(l_m - r_m)
        i_y = r_m * i_x + r_b
        return (i_x, i_y)

    def __pupil(self, eye, eyeProcessor, intersection_x, buffor):

        eyeProcessor.append(eye.getPupil(), eye.getLandmarks(), buffor)
        point = eyeProcessor.getAvgPupil(
            self.eye_screen_w, self.eye_screen_h, buffor)
        point = np.array((int(intersection_x), point[1]))

        return point, buffor

    def estimate(self,
                 image,
                 display,
                 context_id,
                 calibration,
                 fixation_freeze=0.7,
                 freeze_radius=20,
                 offset_x=0,
                 offset_y=0):
        """Function estimating gaze and returning gaze event based on image"""

        event = None
        face_mesh = self.getFeatures(image)
        if not face_mesh:
            return None

        self.face.process(image, face_mesh)

        context = self.GContext.get(context_id, display,
            face = None,
            roi =dp.ScreenROI(
                self.roi_x,
                self.roi_y,
                self.roi_width,
                self.roi_height),
            edges=dp.ScreenROI(285, 105, 80, 15),
            cluster_boundaries=dp.ScreenROI(225, 125, 20, 20),
            buffor=Buffor(200),
            l_pupil=Buffor(20),
            r_pupil=Buffor(20),
            l_eye_buff=Buffor(20),
            r_eye_buff=Buffor(20),
            fixation=Fixation(0, 0, 100))
        context.calibration = calibration

        if not self.face is None:

            if context.face == None:
                x,y,w,h=self.face.getBoundingBox()
                i_w = self.face.image_w
                i_h = self.face.image_h
                context.face = (x,y,w,h,i_w,i_h)


            l_eye = self.face.getLeftEye()
            r_eye = self.face.getRightEye()

            # TODO: check what happens here before with l_pupil
            intersection_x, _ = self.__gaze_intersection(
                l_eye, r_eye, context.l_eye_buff, context.r_eye_buff)
            l_point, l_buffor = self.__pupil(
                l_eye, self.eyeProcessorLeft,  intersection_x, context.l_pupil)
            r_point, r_buffor = self.__pupil(
                r_eye, self.eyeProcessorRight, intersection_x, context.r_pupil)

            context.l_pupil = l_buffor
            context.r_pupil = r_buffor

            compound_point = np.array(((l_point + r_point)/2), dtype=np.uint32)

            blink = l_eye.getBlink() or r_eye.getBlink()
            if blink != True:
                context.gazeBuffor.add(compound_point)

            if blink != True:
                # current face radius
                face_x,face_y,face_w,face_h = self.face.getBoundingBox()
                image_w = self.face.image_w
                image_h = self.face.image_h

                face_w_perc = face_w/image_w
                face_h_perc = face_h/image_h

                # # prev current face radius
                c_face_x,c_face_y,c_face_w,c_face_h,c_image_w,c_image_h = context.face

                c_face_w_perc = c_face_w/c_image_w
                c_face_h_perc = c_face_h/c_image_h

                x,y,w,h=self.face.getBoundingBox()
                i_w = self.face.image_w
                i_h = self.face.image_h
                context.face = (x,y,w,h,i_w,i_h)

                # roi update

                # context.roi.x -= diff_face_x * 500 # current size of virtual display
                # context.roi.y -= diff_face_y * 500 # current size of virtual display
                if abs(face_w_perc/c_face_w_perc - 1.0) > 0.02:
                    context.roi.width  = context.roi.width * abs(face_w_perc/c_face_w_perc)
                    # context.edges.width= context.edges.width * abs(face_w_perc/c_face_w_perc)
                    context.gazeBuffor.flush()
                    # context.calibration = True
                if abs(face_h_perc/c_face_h_perc - 1.0) > 0.02:
                    context.roi.height = context.roi.height* abs(face_h_perc/c_face_h_perc)
                    # context.edges.height= context.edges.height * abs(face_w_perc/c_face_w_perc)
                    context.gazeBuffor.flush()
                    # context.calibration = True

            self.point_screen, roi, cluster = self.screen_man.process(context.gazeBuffor,
                                                                      context.roi,
                                                                      context.edges,
                                                                      self.screen,
                                                                      context.display,
                                                                      context.calibration,
                                                                      (offset_x,
                                                                       offset_y)
                                                                      )

            context.roi = roi
            if cluster:
                x, y, width, height = cluster.getBoundaries()
                context.cluster_boundaries.x = x
                context.cluster_boundaries.y = y
                context.cluster_boundaries.width = width
                context.cluster_boundaries.height = height

            self.GContext.update(context_id, context)

            ###########################################################

            fix = context.fixation.process(
                self.point_screen[0], self.point_screen[1])
            # this should prevent of sudden movement down when blinking - not perfect yet

            if fix > fixation_freeze:
                r = freeze_radius
                if not isInside(self.freezed_point[0], self.freezed_point[1], r, self.point_screen[0], self.point_screen[1]):
                    self.freezed_point = self.point_screen

                event = Gevent(self.freezed_point,
                               blink,
                               fix,
                               l_eye,
                               r_eye,
                               display,
                               context.roi,
                               context.edges,
                               context.cluster_boundaries,
                               context_id)
            else:
                self.freezed_point = self.point_screen
                event = Gevent(self.point_screen,
                               blink,
                               fix,
                               l_eye,
                               r_eye,
                               display,
                               context.roi,
                               context.edges,
                               context.cluster_boundaries,
                               context_id)

        return event

    # def get_contextes(self):
    #     """Function returning contextes"""

    #     return self.GContext.get_contextes()

    # def add_offset(self,x,y):
    #     """Function adding offsets to tracker"""

    #     self.screen_man.push_window(x,y)

    def getFeatures(self, image):
        """Function returning face landmarks"""

        face_mesh = self.finder.find(image)
        return face_mesh
