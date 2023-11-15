import cv2
import sys
import math
import random
import numpy as np
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QImage, QPixmap
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread
import keyboard

from eyeGestures.utils import VideoCapture, Buffor
from eyeGestures.eyegestures import EyeGestures
from eyeGestures.processing import EyeProcess
from screeninfo import get_monitors
from appUtils.dot import DotWidget
from pynput import keyboard


def showEyes(image,face):

    if face is not None:
        cv2.circle(image,face.getLeftPupil()[0],2,(0,0,255),1)
        for point in face.getLeftEye():
            cv2.circle(image,point,2,(0,255,0),1)

        cv2.circle(image,face.getRightPupil()[0],2,(0,0,255),1)
        for point in face.getRightEye():
            cv2.circle(image,point,2,(0,255,0),1)

        for point in face.getLandmarks():
            cv2.circle(image,point,2,(255,0,0),1)            

class Display(QWidget):
    def __init__(self, parent=None):
        super(Display, self).__init__(parent)
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
        if not hasattr(key,'char'):
            return

        if key.char == 'q':
            # Stop listening to the keyboard input and close the application
            self.__run = False
            # self.listener.join()
            self.close()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        super(Display, self).closeEvent(event)

class Screen:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        pass

    def update(self, x, y, width, height):
        pass

class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.frameDisplay = Display()  
        self.pupilLab     = Display()  
        self.noseTilt   = Display()
        self.frameDisplay.show()
        self.pupilLab.show()
        self.noseTilt.show()

        self.eyeProcessor = EyeProcess(250,250)
        
        self.red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.red_dot_widget.show()

        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
        self.__run = True
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

    def on_quit(self,key):
        print(dir(key))
        if not hasattr(key,'char'):
            return

        if key.char == 'q':
            # Stop listening to the keyboard input and close the application
            self.__run = False
            # self.listener.join()
            # self.close()

    def __convertFrame(self,frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.rgbSwapped()
        return p
        
    def __display_left_eye(self,frame):
        frame = frame
        face = self.gestures.getFeatures(frame)
    
        if not face is None:
            whiteboardPupil = np.full((250,250,3),255.0,dtype = np.uint8)
            whiteboardNose  = np.full((500,500,3),255.0,dtype = np.uint8)

            self.eyeProcessor.append(face)
            point = self.eyeProcessor.getAvgPupil(250,250)

            (x,y) = point
            r = math.dist(point,(0,0))
            angle = math.atan2(y,x) * 180/np.pi
            tiltAngle = face.getNose().getHeadTilt()
            new_angle = angle - tiltAngle
            new_angle = np.pi * new_angle / 180 

            new_point = (
                int(r*math.cos(new_angle)), # x
                int(r*math.sin(new_angle))  # y
            )

            # print(f"point:{point}")
            # cv2.circle(whiteboardPupil,point,3,(255,0,0),1)
            print(f"new_point:{new_point}")
            cv2.circle(whiteboardPupil,new_point,3,(0,0,255),1)
    
            self.pupilLab.imshow(
                self.__convertFrame(whiteboardPupil))
    

            for point in face.getNose().getLandmarks():
                cv2.circle(whiteboardNose,point,3,(255,0,0),1)

            self.noseTilt.imshow(
                self.__convertFrame(whiteboardNose))
    
            showEyes(frame,face)            
            self.frameDisplay.imshow(
                self.__convertFrame(frame))

            print(f"HeadDirection: {self.gestures.getHeadDirection()}")
            
            
    def run(self):
        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        ret = True
        while ret and self.__run:

            ret, frame = self.cap.read()     
            
            try:
                self.__display_left_eye(frame)
            except Exception as e:
                print(f"crashed in debug {e}")

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
    