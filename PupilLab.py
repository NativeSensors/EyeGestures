import cv2
import sys
import math
import random
import numpy as np
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QImage, QPixmap
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread
import keyboard

from lab.pupillab import Worker
from lab.components import Screen, ScreenHist, ScreenManager

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
    if abs(tiltAngle) < 30:
        new_point = point
    else:
        new_angle = angle + tiltAngle
        new_angle = np.pi * new_angle / 180 

        new_point = (
            int(r*math.cos(new_angle)), # x
            int(r*math.sin(new_angle))  # y
        )

    return new_point

def showEyes(image,face):

    if face is not None:
        l_eye = face.getLeftEye()
        r_eye = face.getRightEye()

        cv2.circle(image,l_eye.getPupil(),2,(0,0,255),1)
        for point in l_eye.getLandmarks():
            cv2.circle(image,point,2,(0,255,0),1)

        cv2.circle(image,r_eye.getPupil(),2,(0,0,255),1)
        for point in r_eye.getLandmarks():
            cv2.circle(image,point,2,(0,255,0),1)

        for point in face.getLandmarks():
            cv2.circle(image,point,2,(255,0,0),1)            

class Lab:

    def __init__(self):
        
        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)
        # self.noseTilt.show()

        self.step         = 10 
        self.eye_screen_w = 500
        self.eye_screen_h = 500
        self.l_screen_man   = ScreenManager(self.eye_screen_w,self.eye_screen_h)
        self.r_screen_man   = ScreenManager(self.eye_screen_w,self.eye_screen_h)

        self.eyeProcessorLeft  = EyeProcessor(self.eye_screen_w,self.eye_screen_h)
        self.eyeProcessorRight = EyeProcessor(self.eye_screen_w,self.eye_screen_h)
        
        self.red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.red_dot_widget.show()

        self.blue_dot_widget = DotWidget(diameter=100,color = (0,120,255))
        self.blue_dot_widget.show()

        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')        
        self.__run = True

        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

        self.worker = Worker(self.run)

    def on_quit(self,key):
        if not hasattr(key,'char'):
            return

        if key.char == 'q':
            self.__run = False

    def __display_hist(self,whiteboardPupil,hist):
        x_axis,y_axis = hist.getHist()

        bars = int(self.eye_screen_w / self.step)
        for n in range(bars):
            x_val = min(x_axis[n],255)
            y_val = min(y_axis[n],255)
            for m in range(bars):
                y_val = min(y_axis[m],255)
                cv2.rectangle(whiteboardPupil,(self.step*n,self.step*m),(self.step*n + self.step,self.step*m + self.step),(255,255-x_val,255-y_val,50),-1)

    def __display_screen(self,whiteboardPupil,hist,screen):

        (x_min,x_max,y_min,y_max) = hist.getLims()
        (x,y) = (x_min, y_min)
        (w,h) = (x_max - x_min), (y_max - y_min)
        cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(0,0,255),2)
        cv2.putText(whiteboardPupil, f'{w,h}', (x,y), cv2.FONT_HERSHEY_SIMPLEX,  
                   0.5, (0,0,0), 1, cv2.LINE_AA) 
   
        (x,y) = screen.getCenter()
        (w,h) = screen.getWH()  
        cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(255,0,0),2)
        cv2.putText(whiteboardPupil, f'{w,h}', (x,y), cv2.FONT_HERSHEY_SIMPLEX,  
                   0.5, (0,0,0), 1, cv2.LINE_AA) 
    

    def __display_eyeTracker(self,whiteboardPupil,l_point,l_point_screen,r_point,r_point_screen):

        # this is just helper method

        for p in self.l_screen_man.getPointsHistory():
            cv2.circle(whiteboardPupil,p,3,(0,0,255,120),-1)

        for p in self.r_screen_man.getPointsHistory():
            cv2.circle(whiteboardPupil,p,3,(0,255,0,120),-1)

        cv2.circle(whiteboardPupil,l_point,5,(0,0,255),-1)            
        cv2.circle(whiteboardPupil,r_point,5,(0, 0, 255),-1)            

        (w,h) = (self.red_dot_widget.size().width(),self.red_dot_widget.size().height()) 
        self.red_dot_widget.move(l_point_screen[0]-int(w/2),l_point_screen[1]-int(h/2))

        (w,h) = (self.blue_dot_widget.size().width(),self.blue_dot_widget.size().height()) 
        self.blue_dot_widget.move(r_point_screen[0]-int(w/2),r_point_screen[1]-int(h/2))

    def __gaze_intersection(self,l_eye,r_eye):
        l_pupil = l_eye.getPupil()
        l_gaze  = l_eye.getGaze()
        
        r_pupil = r_eye.getPupil()        
        r_gaze  = r_eye.getGaze()

        l_end = l_gaze + l_pupil
        r_end = r_gaze + r_pupil

        l_m = (l_end[1] - l_pupil[1])/(l_end[0] - l_pupil[0])
        r_m = (r_end[1] - r_pupil[1])/(r_end[0] - r_pupil[0])

        l_b = l_end[1] - l_m * l_end[0]
        r_b = r_end[1] - r_m * r_end[0]

        i_x = (r_b - l_b)/(l_m - r_m)
        i_y = r_m * i_x + r_b
        return (i_x,i_y)

    def __display_gaze_intersection(self,display,l_eye,r_eye):
        (i_x,i_y) = self.__gaze_intersection(l_eye,r_eye)

        cv2.circle(display,np.array((i_x,i_y), dtype = np.uint32), 2, (0,0,255),-1)   

    def __display_extended_gaze(self,display,eye,multiplier):
        pupil = eye.getPupil()
        gaze = eye.getGaze()
        
        start_point = (int(pupil[0]),int(pupil[1]))
        (x,y) = (int(gaze[0]),int(gaze[1]))

        angle = math.atan2(y,x) * 180 / np.pi
        r = math.dist(gaze,(0,0)) * multiplier
        
        new_point = (
            int(r*math.cos(np.pi * angle / 180)) + int(pupil[0]), # x
            int(r*math.sin(np.pi * angle / 180)) + int(pupil[1])  # y
        )

        cv2.line(display,start_point,new_point,(255,255,0),1)

    def __display_left_eye(self,frame):
        frame = frame
        face = self.gestures.getFeatures(frame)
    
        if not face is None:
            whiteboardPupil = np.full((self.eye_screen_h,self.eye_screen_w,3),255.0,dtype = np.uint8)
            
            l_eye = face.getLeftEye()
            r_eye = face.getRightEye()
            
            l_pupil = l_eye.getPupil()
            r_pupil = r_eye.getPupil()

            l_position = l_eye.getPos()
            
            intersection_x,_ = self.__gaze_intersection(l_eye,r_eye)

            print(f"l_pupil y:{ l_pupil[1]} l_pupil y - min:{l_pupil[1]-l_position[1]}, l_position[1]:{l_position[1]}")
            # TODO: check what happens here before with l_pupil
            self.eyeProcessorLeft.append( l_pupil,l_eye.getLandmarks())
            self.eyeProcessorRight.append(r_pupil,r_eye.getLandmarks())
            print("processed")

            # This scales pupil move to the screen we observe
            point = self.eyeProcessorLeft.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            print(f"processed l_pupil {point}")
            l_point = (int(intersection_x),point[1])

            point = self.eyeProcessorRight.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            r_point = (int(intersection_x),point[1])

            l_point_screen = self.l_screen_man.process(l_eye,l_point)
            r_point_screen = self.r_screen_man.process(r_eye,r_point)

            print("processed points")
            # here we are having prossed points:

            print("displaying histograms")
            self.__display_hist(whiteboardPupil,self.l_screen_man.getHist())
            self.__display_hist(whiteboardPupil,self.r_screen_man.getHist())

            print("displaying screens")
            self.__display_screen(whiteboardPupil,self.l_screen_man.getHist(),self.l_screen_man.getScreen())
            self.__display_screen(whiteboardPupil,self.r_screen_man.getHist(),self.r_screen_man.getScreen())

            self.__display_eyeTracker(whiteboardPupil,l_point,l_point_screen,r_point,r_point_screen)

            self.__display_extended_gaze(frame,l_eye,10)
            self.__display_extended_gaze(frame,r_eye,10)
            self.__display_gaze_intersection(frame,l_eye,r_eye)
            self.worker.imshow("frame",frame)
            self.worker.imshow("whitebaord",whiteboardPupil)
            self.worker.imshow("left eye",l_eye.getImage())
            self.worker.imshow("right eye",r_eye.getImage())

            # display camera feed
            # showEyes(frame,face)            
            # self.frameDisplay.imshow(
            #     self.__convertFrame(frame))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Lab()
    sys.exit(app.exec_())
    