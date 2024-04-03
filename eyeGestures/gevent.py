"""Module providing a Gaze Events."""
class Gevent:
    """Class representing gaze event, with tracked points scaled to screen, blink and fixation."""

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