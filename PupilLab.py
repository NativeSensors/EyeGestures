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
from eyeGestures.processing import EyeProcessor
from screeninfo import get_monitors
from appUtils.dot import DotWidget
from pynput import keyboard


def rotate(point,face):

    (x,y) = point
    r = math.dist(point,(0,0))
    angle = math.atan2(y,x) * 180/np.pi
    tiltAngle = face.getNose().getHeadTilt()
    if abs(tiltAngle) < 5:
        tiltAngle = 0
    new_angle = angle + tiltAngle
    new_angle = np.pi * new_angle / 180 

    new_point = (
        int(r*math.cos(new_angle)), # x
        int(r*math.sin(new_angle))  # y
    )

    return new_point

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


class ScreenHist:

    def __init__(self,width,height,step):

        self.inc_step = 20

        self.step = step
        self.width = width
        self.height = height

        bars_x = int(self.width/self.step)
        bars_y = int(self.height/self.step)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

    def addPoint(self,point):

        self.axis_x[self.axis_x != 0] -= 1
        self.axis_y[self.axis_y != 0] -= 1

        (x,y) = point
        pos_x = int(x/self.step)
        pos_y = int(y/self.step)
        print(f"x: {x}, pos_x: {pos_x}")
        print(f"y: {y}, pos_y: {pos_y}")

        self.axis_x[pos_x] += self.inc_step
        self.axis_y[pos_y] += self.inc_step

        self.min_x = np.where(self.axis_x > self.inc_step*3)[0][0] * self.step
        self.max_x = np.where(self.axis_x > self.inc_step*3)[0][-1]* self.step
        self.min_y = np.where(self.axis_y > self.inc_step*3)[0][0] * self.step
        self.max_y = np.where(self.axis_y > self.inc_step*3)[0][-1]* self.step

        if not self.min_x is np.NAN:
            self.min_x = int(self.min_x)
        if not self.max_x is np.NAN:
            self.max_x = int(self.max_x)
        if not self.min_y is np.NAN:
            self.min_y = int(self.min_y)
        if not self.max_y is np.NAN:
            self.max_y = int(self.max_y)

    def getLims(self):
        return (self.min_x,self.max_x,self.min_y,self.max_y)

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)

class Screen:

    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.x = x
        self.y = y
        self.width = width 
        self.height = height
        
        pass

    def setSize(self, x = 0, y = 0, width = 0, height = 0):
        self.margin = 0.1
        self.offset_x = int(width * self.margin) 
        
        self.x = int(x) + self.offset_x
        self.y = int(y)
        self.width  = int(width * (1.0 - 2 * self.margin))
        self.height = int(height)

    def update(self, point):
        pass

    def getRect(self):
        return (self.x,self.y,self.width,self.height)

class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.frameDisplay = Display()  
        self.pupilLab     = Display()  
        self.noseTilt     = Display()
        self.histDisplay  = Display()
        self.histDisplay.show()
        self.frameDisplay.show()
        self.pupilLab.show()
        self.noseTilt.show()

        self.eye_screen_w = 500
        self.eye_screen_h = 500
        self.eyeScreen  = Screen()
        self.step = 10 
        self.eyeHist    = ScreenHist(self.eye_screen_w,self.eye_screen_h,self.step)
        self.eyeProcessor = EyeProcessor(self.eye_screen_w,self.eye_screen_h)
        
        self.red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.red_dot_widget.show()

        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
        self.__run = True
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

        self.pointsBuffor = Buffor(100)

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
            whiteboardHist = np.full((self.eye_screen_h,self.eye_screen_w,3),255.0,dtype = np.uint8)
            whiteboardPupil = np.full((self.eye_screen_h,self.eye_screen_w,3),255.0,dtype = np.uint8)
            whiteboardNose  = np.full((500,500,3),255.0,dtype = np.uint8)

            self.eyeProcessor.append(face)
            point = self.eyeProcessor.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            
            # eyeCorner = self.eyeProcessor.getLeftEyeCorner(self.eye_screen_w,self.eye_screen_h)
            # cv2.circle(whiteboardPupil,eyeCorner,3,(0,255,0),1)

            # eyeCenter = self.eyeProcessor.getCenter(self.eye_screen_w,self.eye_screen_h)
            # cv2.circle(whiteboardPupil,eyeCenter,3,(0,255,0),1)

            # screen_x = eyeCorner[0] - 10 # margin of confidence
            # screen_y = eyeCorner[1] + 10 # margin of confidence
            
            # center_x = eyeCenter[0]
            # width = 2 * (center_x - screen_x)

            # self.eyeScreen.setSize(screen_x,screen_y,width ,width * 9/16)
            
            # (x,y,w,h) = self.eyeScreen.getRect()

            # print(f"{(x,y,w,h)}")

            # cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(0,0,255),2)

            # print(f"point:{point}")
            # cv2.circle(whiteboardPupil,point,3,(255,0,0),1)

            closeness = self.eyeProcessor.getHeight() * 20
            print(f"eye closeness {closeness}")

            new_point = rotate(point,face)
            self.pointsBuffor.add((new_point,closeness))
            self.eyeHist.addPoint(new_point)
            x_axis,y_axis = self.eyeHist.getHist()

            bars = int(self.eye_screen_w / self.step)
            for n in range(bars):
                x_val = min(x_axis[n],255)
                y_val = min(y_axis[n],255)
                for m in range(bars):
                    y_val = min(y_axis[m],255)
                    cv2.rectangle(whiteboardPupil,(self.step*n,self.step*m),(self.step*n + self.step,self.step*m + self.step),(255,255-x_val,255-y_val,50),1)
                    # cv2.rectangle(whiteboardPupil,(0,),(self.eye_screen_w,),(0,,0,50),-1)


            # self.eyeScreen.setSize(screen_x,screen_y,width ,width * 9/16)
            
            print(f"Screen rect: {self.eyeHist.getLims()}")
            (x_min,x_max,y_min,y_max) = self.eyeHist.getLims()
            (x,y) = (x_min, y_min)
            (w,h) = (x_max - x_min), (y_max - y_min)
            cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(0,0,255),2)

            # self.histDisplay.imshow(
            #     self.__convertFrame(whiteboardHist))

            for _point,_closeness in self.pointsBuffor.getBuffor():
                cv2.circle(whiteboardPupil,_point,3,(int(_closeness),0,255-int(_closeness)),-1)

            print(f"new_point: {new_point}")
            cv2.circle(whiteboardPupil,new_point,5,(int(closeness),0,255 - int(closeness)),-1)
    
            self.pupilLab.imshow(
                self.__convertFrame(whiteboardPupil))
    
            # for point in face.getNose().getLandmarks():
            #     cv2.circle(whiteboardNose,point,3,(255,0,0),1)

            # self.noseTilt.imshow(
            #     self.__convertFrame(whiteboardNose))
    
            # showEyes(frame,face)            
            self.frameDisplay.imshow(
                self.__convertFrame(frame))

            # print(f"HeadDirection: {self.gestures.getHeadDirection()}")
            
            
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
    