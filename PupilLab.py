import cv2
import sys
import math
import numpy as np

import pyautogui

from PySide2.QtWidgets import QApplication
import keyboard

from lab.pupillab import Worker

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from screeninfo   import get_monitors
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
        self.step         = 10 
        self.eye_screen_w = 500
        self.eye_screen_h = 500
        self.gestures = EyeGestures(self.eye_screen_w,self.eye_screen_h)
        
        self.dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.dot_widget.show()

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

    def __display_screen(self,whiteboardPupil,hist,screen,edges):

        (x_min,x_max,y_min,y_max) = hist.getLims()
        (x,y) = (x_min, y_min)
        (w,h) = (x_max - x_min), (y_max - y_min)
        cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(0,0,255),2)
        cv2.putText(whiteboardPupil, f'{w,h}', (x,y), cv2.FONT_HERSHEY_SIMPLEX,  
                   0.5, (0,0,0), 2, cv2.LINE_AA) 
   
        (x,y) = screen.getCenter()
        (w,h) = screen.getWH()  
        cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(255,0,0),2)
        cv2.putText(whiteboardPupil, f'{w,h}', (x,y), cv2.FONT_HERSHEY_SIMPLEX,  
                   0.5, (0,0,0), 2, cv2.LINE_AA) 

        (x,y,w,h) = edges.getBoundingBox()
        cv2.rectangle(whiteboardPupil,(x,y),(x + w,y + h),(255,125,0),2)    

    def __display_eyeTracker(self, whiteboardPupil, screen_man, point, point_screen, dot_widget):

        # this is just helper method
        for p in screen_man.getPointsHistory():
            cv2.circle(whiteboardPupil,p,3,(0,0,255,120),-1)

        cv2.circle(whiteboardPupil,point,5,(0,0,255),-1)            
        
        (w,h) = (dot_widget.size().width(),dot_widget.size().height()) 
        dot_widget.move(point_screen[0]-int(w/2),point_screen[1]-int(h/2))

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

    def __display_eye(self,frame):
        frame = frame
        event = self.gestures.estimate(frame)

        if not event is None:
            
            if not event.blink:
                self.dot_widget.setColour((int(255*(1-event.fixation)),120,int(255*event.fixation)))
            else:
                pyautogui.moveTo(event.point_screen[0], event.point_screen[1])
                self.dot_widget.setColour((255,120,255))

            whiteboardPupil = np.full((self.eye_screen_h,self.eye_screen_w,3),255.0,dtype = np.uint8)
            
            l_eye = event.l_eye
            r_eye = event.r_eye
            
            # here we are having prossed points:

            self.__display_hist(whiteboardPupil,
                                event.screen_man.getHist())
            
            self.__display_screen(whiteboardPupil, 
                                event.screen_man.getHist(), 
                                event.screen_man.getScreen(), 
                                event.screen_man.getEdgeDetector())

            self.__display_eyeTracker(whiteboardPupil, 
                                      event.screen_man, 
                                      event.point, 
                                      event.point_screen, 
                                      self.dot_widget)


            self.__display_extended_gaze(frame,
                                         event.l_eye,
                                         10)

            self.__display_extended_gaze(frame,
                                         event.r_eye,
                                         10)

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
                self.__display_eye(frame)
            except Exception as e:
                print(f"crashed in debug {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Lab()
    sys.exit(app.exec_())
    