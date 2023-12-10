import sys
import numpy as np

import pyautogui

from PySide2.QtWidgets import QApplication
import keyboard

from lab.pupillab import Worker

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from appUtils.EyeGestureWidget import EyeGestureWidget
from appUtils.dot import DotWidget
from pynput import keyboard

class Lab:

    def __init__(self):
        self.step         = 10 
        self.eye_screen_w = 500
        self.eye_screen_h = 500
        self.gestures = EyeGestures(self.eye_screen_w,self.eye_screen_h)
        
        self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.dot_widget.show()

        # self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
        self.cap = VideoCapture(0)        
        self.__run = True

        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

        self.worker = Worker(self.run)

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
    widget = EyeGestureWidget()
    widget.show()
    Lab()
    sys.exit(app.exec_())
    