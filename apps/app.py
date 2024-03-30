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

from appUtils.dot import DotWidget

class Lab:

    def __init__(self):
        self.step         = 10
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.gestures = EyeGestures(285,115)

        self.calibration_widget = CalibrationWidget()
        self.eyegesture_widget = EyeGestureWidget()
        self.eyegesture_widget.show()
        self.startCalibration()

        self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.dot_widget.show()

        self.cap = VideoCapture(0)

        self.eyegesture_widget.add_close_event(self.calibration_widget.close_event)
        self.eyegesture_widget.add_close_event(self.on_quit)
        self.eyegesture_widget.add_close_event(self.cap.close)
        self.eyegesture_widget.add_close_event(self.dot_widget.close_event)

        self.eyegesture_widget.set_disable_btn(
            self.stopCalibration
        )
        self.eyegesture_widget.set_calibrate_btn(
            self.startCalibration
        )

        self.__run = True

        self.worker = Worker(self.run)

        self.calibrate_left = False
        self.calibrate_right = False
        self.calibrate_top = False
        self.calibrate_bottom = False
        self.window_pushed = False
        self.calibrated = False

        self.push_timer = 500

    def calibrate(self,x,y,fix):
        fix_thresh = 0.4

        if x <= self.monitor.x + 30 and not self.calibrated and fix_thresh < fix:
            self.calibrate_left = True
            self.calibration_widget.disappear_pill("left")
        if x >= self.monitor.width + self.monitor.x - 30 and not self.calibrated and fix_thresh < fix:
            self.calibrate_right = True
            self.calibration_widget.disappear_pill("right")

        if y <= self.monitor.y + 30 and not self.calibrated and fix_thresh < fix:
            self.calibrate_top = True
            self.calibration_widget.disappear_pill("top")
        if y >= self.monitor.height + self.monitor.y - 30 and not self.calibrated and fix_thresh < fix:
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
        event = self.gestures.estimate(frame, 0.7, 200)

        if not event is None:

            #scale down radius when focusing
            self.dot_widget.setColour((int(255*(1-event.fixation)),120,int(255*event.fixation)))
            
            if self.calibrated:
                if event.fixation > 0.7:
                    pyautogui.moveTo(event.point_screen[0]+25, event.point_screen[1]+25)

                if event.blink:
                    pyautogui.moveTo(event.point_screen[0]+25, event.point_screen[1]+25)
                    pyautogui.click()

            self.dot_widget.move(int(event.point_screen[0]),int(event.point_screen[1]))
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