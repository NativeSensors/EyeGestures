import time


class CalibrationPositions:
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

class Calibrator:

    def __init__(self, width, height, start_x, start_y):
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y

        self.prev_x = 0
        self.prev_y = 0

        self.calibration_margin = 200
        self.calibration_steps = []
        self.__set_order()

        self.calibrate_left = False
        self.calibrate_right = False
        self.calibrate_top = False
        self.calibrate_bottom = False

        self.calibration = False
        self.drawn = False
        self.prev_point = None
        self.last_calib = time.time()
        pass

    def __add_left(self):
        self.calibration_steps.append(CalibrationPositions.LEFT)
        return self
    def __add_right(self):
        self.calibration_steps.append(CalibrationPositions.RIGHT)
        return self

    def __add_top(self):
        self.calibration_steps.append(CalibrationPositions.TOP)
        return self

    def __add_bottom(self):
        self.calibration_steps.append(CalibrationPositions.BOTTOM)
        return self

    def __set_order(self):
        if self.start_x < self.width/2 and CalibrationPositions.LEFT not in self.calibration_steps:
            self.__add_left().__add_right()
        elif self.start_x > self.width/2 and CalibrationPositions.RIGHT not in self.calibration_steps:
            self.__add_right().__add_left()

        if self.start_y < self.height/2 and CalibrationPositions.TOP not in self.calibration_steps:
            self.__add_top().__add_bottom()
        elif self.start_y > self.height/2 and CalibrationPositions.BOTTOM not in self.calibration_steps:
            self.__add_bottom().__add_top()

    def add_recalibrate(self,recalibrate_step):

        if recalibrate_step not in self.calibration_steps:
            self.calibration_steps.append(recalibrate_step)

    def get_current_point(self):
        if len(self.calibration_steps) > 0:
            if CalibrationPositions.LEFT == self.calibration_steps[0]:
                return (self.calibration_margin, int(self.height/2))
            elif CalibrationPositions.RIGHT == self.calibration_steps[0]:
                return (self.width - self.calibration_margin, int(self.height/2))
            elif CalibrationPositions.TOP == self.calibration_steps[0]:
                return (int(self.width/2), self.calibration_margin)
            elif CalibrationPositions.BOTTOM == self.calibration_steps[0]:
                return (int(self.width/2), self.height - self.calibration_margin)
        else:
            return (0,0)

    def calibrate(self,x,y,fix):

        if abs(x - self.width/2) > 150 and self.prev_point in [CalibrationPositions.TOP, CalibrationPositions.BOTTOM]:
            if x - self.width/2 < 0:
                self.add_recalibrate(CalibrationPositions.LEFT)
            else:
                self.add_recalibrate(CalibrationPositions.RIGHT)

        if abs(y - self.height/2) > 150  and self.prev_point in [CalibrationPositions.LEFT, CalibrationPositions.RIGHT]:
            if y - self.height/2 < 0:
                self.add_recalibrate(CalibrationPositions.TOP)
            else:
                self.add_recalibrate(CalibrationPositions.BOTTOM)

        self.prev_y = y
        self.prev_x = x
        if len(self.calibration_steps) <= 0:
            self.prev_point = None
            return False

        fixation_thresh = 0.3
        if fix > fixation_thresh and (time.time() - self.last_calib) > 5.0:
            if CalibrationPositions.LEFT == self.calibration_steps[0] and x < self.calibration_margin:
                if CalibrationPositions.LEFT in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationPositions.LEFT)
                self.prev_point = CalibrationPositions.LEFT
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationPositions.RIGHT == self.calibration_steps[0] and x > self.width - self.calibration_margin:
                if CalibrationPositions.RIGHT in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationPositions.RIGHT)
                self.prev_point = CalibrationPositions.RIGHT
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationPositions.TOP == self.calibration_steps[0] and y < self.calibration_margin:
                if CalibrationPositions.TOP in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationPositions.TOP)
                self.prev_point = CalibrationPositions.TOP
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationPositions.BOTTOM == self.calibration_steps[0] and y > self.height - self.calibration_margin:
                if CalibrationPositions.BOTTOM in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationPositions.BOTTOM)
                self.prev_point = CalibrationPositions.BOTTOM
                self.drawn = False
                self.last_calib = time.time()
                return True
            else:
                # TODO: somewhere here is bug breaking entire program
                self.last_calib = time.time()
                self.drawn = False
                self.prev_point = None

                if self.calibration_steps[0] in [CalibrationPositions.RIGHT,CalibrationPositions.LEFT]:
                    if x < self.width/2:
                        if CalibrationPositions.RIGHT in self.calibration_steps:
                            self.calibration_steps.remove(CalibrationPositions.RIGHT)
                        self.calibration_steps.insert(0,CalibrationPositions.RIGHT)
                    else:
                        if CalibrationPositions.LEFT in self.calibration_steps:
                            self.calibration_steps.remove(CalibrationPositions.LEFT)
                        self.calibration_steps.insert(0,CalibrationPositions.LEFT)
                    return True

                if self.calibration_steps[0] is CalibrationPositions.TOP:
                    self.calibration_steps.insert(0,CalibrationPositions.BOTTOM)
                    return True
                else:
                    self.calibration_steps.insert(0,CalibrationPositions.TOP)
                    return True

        self.prev_point = None
        return False

    def calibrated(self):
        return len(self.calibration_steps) <= 0


