"""Module providing a core tracking features."""

import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.Fixation import Fixation
from eyeGestures.utils import Buffor


class Contexter:
    """Class storing contextes"""

    def __init__(self):
        self.context = {}

    def add_context(self, context_id, context):
        """Function allowing to add new context to contexter"""

        if context_id not in self.context:
            self.context[context_id] = context
            return True
        return False

    def remove_context(self, context_id):
        """Function removing context"""
        return self.context.pop(context_id, None) is not None

    def get_context(self, context_id):
        """Function returning context based on id"""
        return self.context.get(context_id, None)

    def update_context(self, context_id, data):
        """Function updating context with new data"""

        if context_id in self.context:
            self.context[context_id] = data
        else:
            self.add_context(context_id, data)
        return True

    def get_number_contexts(self):
        """Function returning number of contexts"""

        return len(self.context)


class Gcontext:
    """Helper class for Gcontext"""

    def __init__(
        self,
        display,
        face,
        roi,
        edges,
        cluster_boundaries,
        gaze_buffor,
        l_pupil,
        r_pupil,
        l_eye_buff,
        r_eye_buff,
        fixation,
        calibration,
    ):

        self.roi = roi
        self.face = face
        self.edges = edges
        self.cluster_boundaries = cluster_boundaries
        self.gaze_buffor = gaze_buffor
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

    def get(
        self,
        context_id,
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
        calibration=False,
    ):
        """Function creating new context or returning if id already exists"""

        context = Gcontext(
            display=display,
            face=face,
            roi=roi,
            edges=edges,
            cluster_boundaries=cluster_boundaries,
            gaze_buffor=buffor,
            l_pupil=l_pupil,
            r_pupil=r_pupil,
            l_eye_buff=l_eye_buff,
            r_eye_buff=r_eye_buff,
            fixation=fixation,
            calibration=calibration,
        )

        if self.contexter.add_context(context_id, context):
            return context
        return self.contexter.get_context(context_id)

    def update(self, context_id, context):
        """Function updating existing context"""

        self.contexter.update_context(context_id, context)
