import cv2
import sys
import math
import random
import numpy as np
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QImage, QPixmap
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread
import keyboard

from eyeGestures.utils import VideoCapture

from eyeGestures.eyegestures import EyeGestures
from screeninfo import get_monitors

from appUtils.dot import DotWidget

from pynput import keyboard

class MoviePlayer(QWidget):
    def __init__(self, parent=None):
        super(MoviePlayer, self).__init__(parent)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

    def imshow(self, q_image):
        # Update the label's pixmap with the new frame
        self.label.setPixmap(QPixmap.fromImage(q_image))
    
    def on_quit(self,key):
        print(dir(key))
        if key.char == 'q':
            # Stop listening to the keyboard input and close the application
            self.close()
            self.listener.join()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        self.frame_processor.stop()
        self.frame_processor.wait()
        super(MoviePlayer, self).closeEvent(event)


class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.blue_dot_widget = DotWidget(diameter=100,color = (120,120,255))
        self.display = MoviePlayer()
        self.pupilLab = MoviePlayer()

        self.red_dot_widget.show()
        self.blue_dot_widget.show()
        self.display.show()
        self.pupilLab.show()
        
        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')

        self.__run = True
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

    def on_quit(self,key):
        print(dir(key))
        if key.char == 'q':
            # Stop listening to the keyboard input and close the application
            self.__run = False
            self.close()
            self.listener.join()

    def __convertFrame(self,frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.rgbSwapped()
        return p
        
    def run(self):
        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        ret = True
        while ret and self.__run:

            ret, frame = self.cap.read()

            if not self.gestures.isCalibrated():
                cPoint = self.gestures.calibrate(frame)
                ePoint = self.gestures.estimate(frame)     
                
                x = int(cPoint[0]*width)
                y = int(cPoint[1]*height)

                self.red_dot_widget.move(x,y)                
            else:
                ePoint = self.gestures.estimate(frame)     
            
            if not np.isnan(ePoint).any():
                x = int(ePoint[0]*width)
                y = int(ePoint[1]*height)
                self.blue_dot_widget.move(x,y)
            
            self.display.imshow(
                self.__convertFrame(frame))

        #show point on sandbox
        # cv2.destroyAllWindows()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread = QThread()
    worker = Worker()
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    thread.start()

    sys.exit(app.exec_())
    