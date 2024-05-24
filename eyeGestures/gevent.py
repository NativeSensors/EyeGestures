"""Module providing a Gaze Events."""


class Gevent:
    """Class representing gaze event, with tracked points scaled to screen, blink and fixation."""

    def __init__(self,
                 point,
                 blink,
                 fixation,
                 l_eye = None,
                 r_eye = None,
                 screen_man = None,
                 roi = None,
                 edges = None,
                 cluster = None,
                 context = None):

        self.point = point
        self.blink = blink
        self.fixation = fixation

        # ALL DEBUG DATA
        self.roi = roi
        self.edges = edges
        self.l_eye = l_eye
        self.r_eye = r_eye
        self.cluster = cluster
        self.context = context
        self.screen_man = screen_man


class Cevent:
    """Class representing gaze event, with tracked points scaled to screen, blink and fixation."""

    def __init__(self,
                 point,
                 acceptance_radius,
                 calibration_radius,
                 calibration = False):

        self.point = point
        self.acceptance_radius = acceptance_radius
        self.calibration_radius = calibration_radius
        self.calibration = calibration
