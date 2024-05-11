"""Module providing a processing pupil position to gaze direction."""

import numpy as np


class EyeProcessor:
    """Class providing processing for eye to obtain gaze direction."""

    def __init__(self, scale_w=250, scale_h=250):
        self.scale_w = scale_w
        self.scale_h = scale_h
        self.pupil = None
        self.landmarks = None

    def append(self, eye, pupilBuffor):
        """Function appending new pupil point to tracker."""

        self.pupil = eye.getPupil()
        x,y,width,height = eye.getBoundingBox()
        # height = height/2

        # print(width,height)
        pupilBuffor.add(
            self.__convertPoint(self.pupil,
                                width=self.scale_w, height=self.scale_h,
                                scale_w=width, scale_h=height,
                                offset=(x,y)))

    def __convertPoint(self, point,
                       width=1.0,
                       height=1.0,
                       scale_w=1.0,
                       scale_h=1.0,
                       offset=(0.0, 0.0)):
        (min_x, min_y) = offset
        x = int(((point[0]-min_x)/scale_w)*width)
        y = int(((point[1]-min_y)/scale_h)*height)
        return (x, y)

    def getAvgPupil(self, width, height, pupilBuffor):
        """Function returning average point based on tracked."""

        if not width is None and not height is None:
            _retPupil = self.__convertPoint(pupilBuffor.getAvg(),
                                            width=width, height=height,
                                            scale_w=self.scale_w, scale_h=self.scale_h)
        else:
            _retPupil = pupilBuffor.getAvg()

        return _retPupil
