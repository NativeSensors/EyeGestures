import os
import cv2
import sys
import time

import pyautogui
from screeninfo import get_monitors
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QObject, QThread

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from appUtils.EyeGestureWidget import EyeGestureWidget
from appUtils.CalibrationWidget import CalibrationWidget
from apps.appUtils.dot import DotWidget
from appUtils.data_saver import DataManager

class CalibrationTypes:
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class Worker(QObject):

    def __init__(self,thread):
        super().__init__()

        self.__displayPool = dict()
        self.__thread = thread

        self.__run = True

        self.thread = QThread()
        self.moveToThread(self.thread)

        self.thread.started.connect(self.run)
        self.thread.start()

    def on_quit(self):
        if self.__run == True:
            self.__run = False
            self.thread.quit()
            self.thread.wait()
            print("worker stopped")

    def run(self):
        while self.__run:
            self.__thread()

class Calibrator:

    def __init__(self,width,height,start_x, start_y, show, disappear):
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y

        self.prev_x = 0
        self.prev_y = 0

        self.calibration_margin = 200
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
        self.prev_point = None
        self.last_calib = time.time()
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

        if abs(x - self.width/2) > 150 and self.prev_point in [CalibrationTypes.TOP, CalibrationTypes.BOTTOM]:
            if x - self.width/2 < 0:
                self.add_recalibrate(CalibrationTypes.LEFT)
            else:
                self.add_recalibrate(CalibrationTypes.RIGHT)

        if abs(y - self.height/2) > 150  and self.prev_point in [CalibrationTypes.LEFT, CalibrationTypes.RIGHT]:
            if y - self.height/2 < 0:
                self.add_recalibrate(CalibrationTypes.TOP)
            else:
                self.add_recalibrate(CalibrationTypes.BOTTOM)

        self.prev_y = y
        self.prev_x = x
        if len(self.calibration_steps) <= 0:
            self.prev_point = None
            return False

        self.display_next_calibration_target()
        fixation_thresh = 0.3
        if fix > fixation_thresh and (time.time() - self.last_calib) > 5.0:
            if CalibrationTypes.LEFT == self.calibration_steps[0] and x < self.calibration_margin:
                self.disappear(self.calibration_steps[0])
                if CalibrationTypes.LEFT in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationTypes.LEFT)
                self.prev_point = CalibrationTypes.LEFT
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationTypes.RIGHT == self.calibration_steps[0] and x > self.width - self.calibration_margin:
                self.disappear(self.calibration_steps[0])
                if CalibrationTypes.RIGHT in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationTypes.RIGHT)
                self.prev_point = CalibrationTypes.RIGHT
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationTypes.TOP == self.calibration_steps[0] and y < self.calibration_margin:
                self.disappear(self.calibration_steps[0])
                if CalibrationTypes.TOP in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationTypes.TOP)
                self.prev_point = CalibrationTypes.TOP
                self.drawn = False
                self.last_calib = time.time()
                return True
            elif CalibrationTypes.BOTTOM == self.calibration_steps[0] and y > self.height - self.calibration_margin:
                self.disappear(self.calibration_steps[0])
                if CalibrationTypes.BOTTOM in self.calibration_steps:
                    self.calibration_steps.remove(CalibrationTypes.BOTTOM)
                self.prev_point = CalibrationTypes.BOTTOM
                self.drawn = False
                self.last_calib = time.time()
                return True
            else:
                # TODO: somewhere here is bug breaking entire program
                self.last_calib = time.time()
                self.disappear(self.calibration_steps[0])
                self.drawn = False
                self.prev_point = None

                if self.calibration_steps[0] in [CalibrationTypes.RIGHT,CalibrationTypes.LEFT]:
                    if x < self.width/2:
                        if CalibrationTypes.RIGHT in self.calibration_steps:
                            self.calibration_steps.remove(CalibrationTypes.RIGHT)
                        self.calibration_steps.insert(0,CalibrationTypes.RIGHT)
                    else:
                        if CalibrationTypes.LEFT in self.calibration_steps:
                            self.calibration_steps.remove(CalibrationTypes.LEFT)
                        self.calibration_steps.insert(0,CalibrationTypes.LEFT)
                    return True

                if self.calibration_steps[0] is CalibrationTypes.TOP:
                    self.calibration_steps.insert(0,CalibrationTypes.BOTTOM)
                    return True
                else:
                    self.calibration_steps.insert(0,CalibrationTypes.TOP)
                    return True

        self.prev_point = None
        return False

    def calibrated(self):
        return len(self.calibration_steps) <= 0

    def clear_up(self):
        for calibration_step in self.calibration_steps:
            self.disappear(calibration_step)


class Lab:

    def __init__(self,main_quit):
        self.step         = 10
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.sensitivity_roi_width = int(80)
        self.sensitivity_roi_height = int(8)
        self.gestures = EyeGestures(roi_y = 40, roi_width=int(80),roi_height=int(8))

        self.calibration_widget = CalibrationWidget()
        self.calibration_widget.disappear()
        self.eyegesture_widget = EyeGestureWidget(
            start_cb = self.start,
            stop_cb = self.stop,
            update_fixation_cb = self.update_fixation,
            update_radius_cb = self.update_radius,
            cursor_visible = self.cursor_visible,
            cursor_not_visible = self.cursor_not_visible,
            screen_recording_enable = self.screen_recording_enable,
            screen_recording_disabled = self.screen_recording_disabled,
            update_sensitivity_y_cb = self.update_sensitivity_y_cb,
            update_sensitivity_x_cb = self.update_sensitivity_x_cb,
            live_viewer_OFF = self.live_viewer_OFF,
            live_viewer_ON = self.live_viewer_ON,
        )
        self.eyegesture_widget.show()

        self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.dot_widget.show()

        self.cap = VideoCapture(0)

        self.eyegesture_widget.add_close_event(self.cap.close)
        self.eyegesture_widget.add_close_event(self.dot_widget.close_event)
        self.eyegesture_widget.add_close_event(self.calibration_widget.close_event)
        self.eyegesture_widget.add_close_event(self.on_quit)
        self.eyegesture_widget.add_close_event(main_quit)

        self.__run = False
        self.power_off = False

        self.worker = Worker(self.run)

        self.calibrator = None
        self.calibration = False
        self.iterations = 0

        self.fixation = 0.8
        self.radius   = 400

        self.live_view = False

        self.dataSavingMan = DataManager()

    def update_sensitivity_y_cb(self, value):
        self.sensitivity_roi_height = value

    def update_sensitivity_x_cb(self, value):
        self.sensitivity_roi_width = value

    def start(self):
        self.dataSavingMan = DataManager()
        self.gestures = EyeGestures(
            roi_y = 40,
            roi_width=self.sensitivity_roi_width ,
            roi_height=self.sensitivity_roi_height
        )
        self.dataSavingMan.enable_screenshots()
        self.calibrator = None
        self.__run = True

    def stop(self):
        self.dataSavingMan.disable_screenshots()
        self.__run = False
        if self.calibrator:
            self.calibrator.clear_up()
        pass

    def live_viewer_ON(self):
        self.live_view = True

    def live_viewer_OFF(self):
        self.live_view = False

    def cursor_visible(self):
        self.dot_widget.show()
        pass

    def cursor_not_visible(self):
        self.dot_widget.hide()
        pass

    def screen_recording_enable(self):
        self.dataSavingMan.enable_screenshots()
        pass

    def screen_recording_disabled(self):
        self.dataSavingMan.disable_screenshots()
        pass

    def update_fixation(self,fixation):
        self.fixation = fixation

    def update_radius(self,radius):
        self.radius = radius

    def on_quit(self):
        self.stop()
        self.__run = False
        self.power_off = True
        self.worker.on_quit()

    def save_data(self,event,rois_to_save):
        if not self.calibrator.calibrated():
            filename = f"calib_{self.eyegesture_widget.get_text()}"
        else:
            filename = f"{self.eyegesture_widget.get_text()}"
        self.dataSavingMan.add_frame(filename,
                                        event,
                                        rois_to_save,
                                        self.sensitivity_roi_width,
                                        self.sensitivity_roi_height)

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

        if not event is None:
            rois_to_save = self.eyegesture_widget.get_rois_w_detection(cursor_x,cursor_y)

            (w,h) = (self.dot_widget.size().width(),self.dot_widget.size().height()) 
            self.dot_widget.move(event.point_screen[0]-int(w/2),event.point_screen[1]-int(h/2))
            self.save_data(event,rois_to_save)

            # during calibration update visuals
            if not self.calibrator.calibrated() or self.live_view:
                self.eyegesture_widget.update_fixation(event.fixation)
                self.eyegesture_widget.update_dot_viewer(int(cursor_x),int(cursor_y))

    def run(self):
        fps_cap = 30
        self.prev_frame = time.time()
        while not self.power_off:
            ret = True
            while ret and self.__run:
                if (time.time() - self.prev_frame) > 1.0/fps_cap:
                    ret, frame = self.cap.read()

                    try:
                        self.__display_eye(frame)
                    except Exception as e:
                        print(f"crashed in debug {e}")
                    self.prev_frame = time.time()
        print("Exiting main loop.")

if __name__ == '__main__':
    # x_prev = 117
    # x = 0
    # y = 1440
    # c = Calibrator(2560,1440,0,0, lambda x : None, lambda x : None)
    # c.prev_x = 117
    # c.calibrate(x,y,0.3,True)
    app = QApplication(sys.argv)
    lab = Lab(app.quit)
    sys.exit(app.exec_())