"""Module providing a core tracking features."""

import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.Fixation import Fixation
from eyeGestures.utils import Buffor


class Contexter:
    """Class storing contextes"""

    def __init__(self):
        self.context = dict()

    def addContext(self, context_id, object):
        """Function allowing to add new context to contexter"""

        if context_id not in self.context.keys():
            self.context[context_id] = object
            return True
        return False

    def rmContext(self, context_id):
        """Function allowing to removes context from contexter"""

        if context_id in self.context.keys():
            del self.context[context_id]
            return True
        return False

    def getContext(self, context_id):
        """Function returning context based on id"""

        if context_id in self.context.keys():
            return self.context[context_id]
        return None

    def updateContext(self, context_id, data):
        """Function updating context with new data"""

        if context_id in self.context.keys():
            self.context[context_id] = data
            return True
        self.addContext(context_id, data)
        return True

    def getNumberContextes(self):
        """Function returning number of contextes"""

        return len(self.context.keys())


class Gcontext:
    """Helper class for Gcontext"""

    def __init__(self,
                 display,
                 face,
                 roi,
                 edges,
                 cluster_boundaries,
                 gazeBuffor,
                 l_pupil,
                 r_pupil,
                 l_eye_buff,
                 r_eye_buff,
                 fixation,
                 calibration):

        self.roi = roi
        self.face = face
        self.edges = edges
        self.cluster_boundaries = cluster_boundaries
        self.gazeBuffor = gazeBuffor
        self.l_pupil = l_pupil
        self.r_pupil = r_pupil
        self.l_eye_buff = l_eye_buff
        self.r_eye_buff = r_eye_buff
        self.display = display
        self.fixation = fixation
        self.calibration = calibration


class GazeContext:
    """Context wrapper for gaze tracker application"""

    def __init__(self):
        self.contexter = Contexter()

    def get(self,
            id,
            display,
            face=None,
            roi=dp.ScreenROI(285, 105, 80, 15),
            edges=dp.ScreenROI(285, 105, 80, 15),
            cluster_boundaries=dp.ScreenROI(225, 125, 20, 20),
            buffor=Buffor(200),
            l_pupil=Buffor(20),
            r_pupil=Buffor(20),
            l_eye_buff=Buffor(20),
            r_eye_buff=Buffor(20),
            fixation=Fixation(0, 0, 100),
            calibration=False):
        """Function creating new context or returning if id already exists"""

        context = Gcontext(display=display,
                           face=face,
                           roi=roi,
                           edges=edges,
                           cluster_boundaries=cluster_boundaries,
                           gazeBuffor=buffor,
                           l_pupil=l_pupil,
                           r_pupil=r_pupil,
                           l_eye_buff=l_eye_buff,
                           r_eye_buff=r_eye_buff,
                           fixation=fixation,
                           calibration=calibration)

        if self.contexter.addContext(id, context):
            return context
        else:
            return self.contexter.getContext(id)

    def update(self,
               id,
               context):
        """Function updating existing context"""

        self.contexter.updateContext(id, context)
