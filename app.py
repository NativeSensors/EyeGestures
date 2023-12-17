import sys

import pyautogui
from screeninfo import get_monitors

from PySide2.QtWidgets import QApplication
import keyboard

from lab.pupillab import Worker

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from appUtils.EyeGestureWidget import EyeGestureWidget
from appUtils.CalibrationWidget import CalibrationWidget
from appUtils.dot import DotWidget
from pynput import keyboard

import cv2

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
        
        self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.calibration_widget = CalibrationWidget()
        self.eyegesture_widget = EyeGestureWidget()
        self.eyegesture_widget.show()
        self.dot_widget.show()

        self.eyegesture_widget.set_disable_btn(
            self.stopCalibration
        )
        self.eyegesture_widget.set_calibrate_btn(
            self.startCalibration
        )

        # self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
        self.cap = VideoCapture(0)        
        self.startCalibration()
        
        self.__run = True

        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

        self.worker = Worker(self.run)

        self.calibrate_left = False
        self.calibrate_right = False
        self.calibrate_top = False
        self.calibrate_bottom = False
        self.calibrated = False

    def calibrate(self,x,y):
        print(self.calibrate_bottom, self.calibrate_top, self.calibrate_left, self.calibrate_right )
        
        if x <= self.monitor.x and not self.calibrated:
            self.calibrate_left = True
        if x >= self.monitor.width + self.monitor.x and not self.calibrated:
            self.calibrate_right = True
    
        if y <= self.monitor.y and not self.calibrated:
            self.calibrate_top = True
        if y >= self.monitor.height + self.monitor.y - 10 and not self.calibrated:
            self.calibrate_bottom = True


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
        print("press starCalibration")
        self.calibrated = False
        self.gestures.start_calibration()
        self.calibration_widget.show_again()
        self.eyegesture_widget.set_calibrate()
        pass

    def stopCalibration(self):
        print("press stopCalibration")
        self.gestures.stop_calibration()
        self.calibration_widget.disappear()
        pass

    def on_quit(self,key):
        if not hasattr(key,'char'):
            return

        if key.char == 'q':
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
            self.dot_widget.move(event.point_screen[0]-int(w/2),event.point_screen[1]-int(h/2))
            self.calibrate(event.point_screen[0], event.point_screen[1])
                
            # here we are having prossed points:            
            
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
    