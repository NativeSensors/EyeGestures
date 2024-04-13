import os
import cv2
import sys

import pyautogui
from screeninfo import get_monitors
from PySide2.QtWidgets import QApplication

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}\\..')

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from appUtils.EyeGestureWidget import EyeGestureWidget
from appUtils.CalibrationWidget import CalibrationWidget
from lab.pupillab import Worker
from appUtils.dot_windows import WindowsCursor
from appUtils.data_saver import save_gaze_data_to_csv

class CalibrationTypes:
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

class Calibrator:

    def __init__(self,width,height,start_x, start_y, show, disappear):
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y

        self.prev_x = 0
        self.prev_y = 0

        self.calibration_margin = 100
        self.calibration_steps = []
        self.__set_order()
        self.show = show
        self.disappear = disappear

        self.calibrate_left = False
        self.calibrate_right = False
        self.calibrate_top = False
        self.calibrate_bottom = False

        self.calibration = False
        self.drawn = False
        pass

    def display_next_calibration_target(self):
        if len(self.calibration_steps) > 0 and not self.drawn:
            self.drawn = True
            self.show(self.calibration_steps[0])

    def __add_left(self):
        self.calibration_steps.append(CalibrationTypes.LEFT)
        return self
    def __add_right(self):
        self.calibration_steps.append(CalibrationTypes.RIGHT)
        return self

    def __add_top(self):
        self.calibration_steps.append(CalibrationTypes.TOP)
        return self

    def __add_bottom(self):
        self.calibration_steps.append(CalibrationTypes.BOTTOM)
        return self

    def __set_order(self):
        if self.start_x < self.width/2 and CalibrationTypes.LEFT not in self.calibration_steps:
            self.__add_left().__add_right()
        elif self.start_x > self.width/2 and CalibrationTypes.RIGHT not in self.calibration_steps:
            self.__add_right().__add_left()

        if self.start_y < self.height/2 and CalibrationTypes.TOP not in self.calibration_steps:
            self.__add_top().__add_bottom()
        elif self.start_y > self.height/2 and CalibrationTypes.BOTTOM not in self.calibration_steps:
            self.__add_bottom().__add_top()

    def add_recalibrate(self,recalibrate_step):

        if recalibrate_step not in self.calibration_steps:
            self.calibration_steps.append(recalibrate_step)


    def calibrate(self,x,y,fix):

        if abs(x - self.prev_x) > 200:
            if x - self.prev_x < 0:
                self.add_recalibrate(CalibrationTypes.LEFT)
            else:
                self.add_recalibrate(CalibrationTypes.RIGHT)

        if abs(y - self.prev_y) > 200:
            if y - self.prev_y < 0:
                self.add_recalibrate(CalibrationTypes.TOP)
            else:
                self.add_recalibrate(CalibrationTypes.BOTTOM)

        self.prev_y = y
        self.prev_x = x
        if len(self.calibration_steps) <= 0:
            return False

        self.display_next_calibration_target()
        fixation_thresh = 0.4
        if CalibrationTypes.LEFT == self.calibration_steps[0] and x < self.calibration_margin and fix > fixation_thresh:
            self.disappear(self.calibration_steps[0])
            self.calibration_steps.pop(0)
            self.drawn = False
            return True
        elif CalibrationTypes.RIGHT == self.calibration_steps[0] and x > self.width - self.calibration_margin and fix > fixation_thresh:
            self.disappear(self.calibration_steps[0])
            self.calibration_steps.pop(0)
            self.drawn = False
            return True
        elif CalibrationTypes.TOP == self.calibration_steps[0] and y < self.calibration_margin and fix > fixation_thresh:
            self.disappear(self.calibration_steps[0])
            self.calibration_steps.pop(0)
            self.drawn = False
            return True
        elif CalibrationTypes.BOTTOM == self.calibration_steps[0] and y > self.height - self.calibration_margin and fix > fixation_thresh:
            self.disappear(self.calibration_steps[0])
            self.calibration_steps.pop(0)
            self.drawn = False
            return True

        return False

    def calibrated(self):
        print(len(self.calibration_steps))
        return len(self.calibration_steps) <= 0

    def clear_up(self):
        for calibration_step in self.calibration_steps:
            self.disappear(calibration_step)


class Lab:

    def __init__(self):
        self.step         = 10
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.gestures = EyeGestures(285,115)

        self.calibration_widget = CalibrationWidget()
        self.calibration_widget.disappear()
        self.eyegesture_widget = EyeGestureWidget(
            self.start,
            self.stop,
            self.update_fixation,
            self.update_radius)

        self.eyegesture_widget.show()

        self.dot_widget = WindowsCursor(50, 2)

        self.cap = VideoCapture(0)

        self.eyegesture_widget.add_close_event(self.calibration_widget.close_event)
        self.eyegesture_widget.add_close_event(self.on_quit)
        self.eyegesture_widget.add_close_event(self.cap.close)
        self.eyegesture_widget.add_close_event(self.dot_widget.close_event)

        self.__run = False
        self.power_off = False

        self.worker = Worker(self.run)

        self.calibrator = None
        self.calibration = False
        self.iterations = 0

        self.fixation = 0.8
        self.radius   = 400

    def start(self):
        self.calibrator = None
        self.__run = True

    def stop(self):
        self.__run = False
        self.calibrator.clear_up()
        pass

    def update_fixation(self,fixation):
        self.fixation = fixation

    def update_radius(self,radius):
        self.radius = radius

    def on_quit(self):
        self.__run = False
        self.power_off = True

    def save_data(self,event):
        filename = f"{self.eyegesture_widget.get_text()}.csv"
        save_gaze_data_to_csv(filename,event)

    def __display_eye(self,frame):
        frame = cv2.flip(frame, 1)
        cursor_x, cursor_y = 0, 0
        event = self.gestures.estimate(
            frame,
            "main",
            self.calibration, # set calibration - switch to False to stop calibration
            self.monitor.width,
            self.monitor.height,
            0, 0, 0.8, 10)

        cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]

        if self.iterations < 3:
            self.iterations += 1
            return None

        if self.calibrator:
            self.calibration = self.calibrator.calibrate(cursor_x,cursor_y,event.fixation)
        else:
            self.calibrator = Calibrator(self.monitor.width,self.monitor.height,cursor_x,cursor_y,self.calibration_widget.show_pill,self.calibration_widget.disappear_pill)
            self.calibration = self.calibrator.calibrate(cursor_x,cursor_y,event.fixation)
        # frame = pygame.transform.scale(frame, (400, 400))

        print(f"self.calibration: {self.calibrator.calibrated()}")
        if self.calibrator.calibrated():
            self.dot_widget.hide()
        else:
            self.dot_widget.show()

        if not event is None:
            self.save_data(event)
            self.eyegesture_widget.update_fixation(event.fixation)

            #scale down radius when focusing
            radius = int(60 - (50 * event.fixation))
            self.dot_widget.set_radius(radius)

            if self.calibration:
                if event.fixation > 0.7:
                    pyautogui.moveTo(cursor_x + radius/2,  cursor_y + radius/2)

                if event.blink:
                    pyautogui.moveTo(cursor_x + radius/2,  cursor_y + radius/2)
                    pyautogui.click()

            self.dot_widget.move(int(cursor_x),int(cursor_y))

    def run(self):
        while not self.power_off:
            ret = True
            while ret and self.__run:

                ret, frame = self.cap.read()

                try:
                    self.__display_eye(frame)
                except Exception as e:
                    print(f"crashed in debug {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lab = Lab()
    sys.exit(app.exec_())