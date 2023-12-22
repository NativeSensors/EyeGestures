import sys

import pyautogui
from screeninfo import get_monitors
from PySide2.QtWidgets import QApplication
from lab.pupillab import Worker
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from appUtils.EyeGestureWidget import EyeGestureWidget
from appUtils.CalibrationWidget import CalibrationWidget

import cv2

import platform

from appUtils.dot import DotWidget

class Lab:

    def __init__(self):
        self.step         = 10
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.eye_screen_w = 500
        self.eye_screen_h = 500
        self.gestures = EyeGestures(self.monitor.width,
                                    self.monitor.height,
                                    self.eye_screen_w,
                                    self.eye_screen_h,
                                    self.monitor.x,
                                    self.monitor.y)

        self.calibration_widget = CalibrationWidget()
        self.eyegesture_widget = EyeGestureWidget()
        self.eyegesture_widget.show()

        if platform.system() == "Windows":
            self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
            self.dot_widget.show()
        else:
            green = RGBA(0, 100, 0, 128) # green
            self.dot_widget = WindowsCircle(50, 2, green, self.monitor.width, self.monitor.height)

        self.cap = VideoCapture(0)

        self.eyegesture_widget.add_close_event(self.dot_widget.close_event)
        self.eyegesture_widget.add_close_event(self.calibration_widget.close_event)
        self.eyegesture_widget.add_close_event(self.on_quit)
        self.eyegesture_widget.add_close_event(self.cap.close)

        self.eyegesture_widget.set_disable_btn(
            self.stopCalibration
        )
        self.eyegesture_widget.set_calibrate_btn(
            self.startCalibration
        )

        self.startCalibration()
        self.__run = True

        self.worker = Worker(self.run)

        self.calibrate_left = False
        self.calibrate_right = False
        self.calibrate_top = False
        self.calibrate_bottom = False
        self.calibrated = False

    def calibrate(self,x,y,fix):
        fix_thresh = 0.4

        if x <= self.monitor.x + 10 and not self.calibrated and fix_thresh < fix:
            self.calibrate_left = True
            self.calibration_widget.disappear_pill("left")
        if x >= self.monitor.width + self.monitor.x - 10 and not self.calibrated and fix_thresh < fix:
            self.calibrate_right = True
            self.calibration_widget.disappear_pill("right")


        if y <= self.monitor.y + 10 and not self.calibrated and fix_thresh < fix:
            self.calibrate_top = True
            self.calibration_widget.disappear_pill("top")
        if y >= self.monitor.height + self.monitor.y - 10 and not self.calibrated and fix_thresh < fix:
            self.calibrate_bottom = True
            self.calibration_widget.disappear_pill("bottom")


        if( self.calibrate_bottom
            and self.calibrate_top
            and self.calibrate_left
            and self.calibrate_right
            and not self.calibrated):

            self.calibrated = True
            self.calibrate_bottom = False
            self.calibrate_top = False
            self.calibrate_left = False
            self.calibrate_right = False

            self.stopCalibration()

    def startCalibration(self):
        self.calibrated = False
        self.gestures.start_calibration()
        self.calibration_widget.show_again()
        self.eyegesture_widget.set_calibrate()
        pass

    def stopCalibration(self):
        self.gestures.stop_calibration()
        self.calibration_widget.disappear()
        pass

    def on_quit(self):
        self.__run = False

    def __display_eye(self,frame):
        frame = cv2.flip(frame, 1)
        event = self.gestures.estimate(frame)

        if not event is None:

            if not event.blink:
                self.dot_widget.setColour((int(255*(1-event.fixation)),120,int(255*event.fixation)))
            else:
                pyautogui.moveTo(event.point_screen[0], event.point_screen[1])
                self.dot_widget.setColour((255,120,255))

            (w,h) = (self.dot_widget.size().width(),self.dot_widget.size().height())
            print("moving cursor")
            self.dot_widget.move(event.point_screen[0]-int(w/2),event.point_screen[1]-int(h/2))

            self.calibrate(event.point_screen[0], event.point_screen[1], event.fixation)

    def run(self):
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