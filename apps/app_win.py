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

class Lab:

    def __init__(self):
        self.step         = 10
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.gestures = EyeGestures(285,115)

        self.calibration_widget = CalibrationWidget()
        self.eyegesture_widget = EyeGestureWidget()
        self.eyegesture_widget.show()
        self.startCalibration()

        self.dot_widget = WindowsCursor(50, 2)

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
        self.calibration = False

    def calibrate(self,x,y,fix):
        fix_thresh = 0.4

        if x <= self.monitor.x + 30 and not self.calibration and fix_thresh < fix:
            self.calibrate_left = True
            self.calibration_widget.disappear_pill("left")
        if x >= self.monitor.width + self.monitor.x - 30 and not self.calibration and fix_thresh < fix:
            self.calibrate_right = True
            self.calibration_widget.disappear_pill("right")


        if y <= self.monitor.y + 30 and not self.calibration and fix_thresh < fix:
            self.calibrate_top = True
            self.calibration_widget.disappear_pill("top")
        if y >= self.monitor.height + self.monitor.y - 30 and not self.calibration and fix_thresh < fix:
            self.calibrate_bottom = True
            self.calibration_widget.disappear_pill("bottom")


        if( self.calibrate_bottom
            and self.calibrate_top
            and self.calibrate_left
            and self.calibrate_right
            and not self.calibration):

            self.calibration = True
            self.calibrate_bottom = False
            self.calibrate_top = False
            self.calibrate_left = False
            self.calibrate_right = False

            self.stopCalibration()

    def startCalibration(self):
        self.calibration = True
        pass

    def stopCalibration(self):
        self.calibration = False
        pass

    def on_quit(self):
        self.__run = False

    def __display_eye(self,frame):
        frame = cv2.flip(frame, 1)
        cursor_x, cursor_y = 0, 0
        event = self.gestures.estimate(
            frame,
            "main",
            self.calibrate, # set calibration - switch to False to stop calibration
            self.monitor.width,
            self.monitor.height,
            0, 0, 0.8,10)

        cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
        # frame = pygame.transform.scale(frame, (400, 400))

        if not event is None:

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