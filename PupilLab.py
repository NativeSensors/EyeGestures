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

class EyeDisplay:

    def __init__(self):
        self.PupilBuffor = Buffor(20)
        pass

    def update(self,face,sWidth,sHeigh)
        self.pupil = face.getLeftPupil()[0]
        self.landmarks = face.getLeftEye()

        self.PupilBuffor.add(self.pupil)
        # self.PupilBuffor.add(self.__adjPoint(
        #     self.pupil,sWidth,sHeigh
        # ))

        # get center: 
        self.min_x = np.min(landmarks[:,0])
        self.max_x = np.max(landmarks[:,0])
        self.min_y = np.min(landmarks[:,1])
        self.max_y = np.max(landmarks[:,1])

        self.center = ((min_x + max_x)/2,
                        (min_y + max_y)/2)

        self.width = max_x - min_x 
        self.height = 20

    def __adjPoint(self,point,width,height):
        x = int(((point-min_x)/self.width)*width)
        y = int(((point-min_y)/self.height)*height)
        return (x,y)

    def draw(self,image,width,height):
        cv2.circle(image,
            np.array(
                self.__adjPoint(self.center,width,height),
                dtype= np.uint8),
            3,(0,255,0),1)
            
        cv2.circle(image,
            np.array(
                self.__adjPoint(self.PupilBuffor.getAvg(),width,height),
                dtype= np.uint8),
            3,(0,255,0),1)

        for point in self.landmarks:
            cv2.circle(image,
                np.array(
                    self.__adjPoint(point,width,height)
                ,dtype= np.uint8),
                3,(0,0,255),1)

        return image



class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.frameDisplay = Display()  
        self.pupilLab     = Display()  
        self.pupilAdjLab   = Display()
        self.frameDisplay.show()
        self.pupilLab.show()
        self.pupilAdjLab.show()

        self.eyeDisplay = EyeDisplay()
        
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
            whiteboard = np.full((250,250,3),255.0,dtype = np.uint8)
            
            self.eyeDisplay.update(face,250,250)
            self.eyeDisplay.draw(whiteboard,image,250,250)
            self.pupilLab.imshow(
                self.__convertFrame(whiteboard))

            ###################################################################################3
            # get center: 
            whiteboardAdj = np.full((250,250,3),255.0,dtype = np.uint8)
            min_x = np.min(landmarks[:,0])
            max_x = np.max(landmarks[:,0])
            min_y = np.min(landmarks[:,1])
            max_y = np.max(landmarks[:,1])

            center_x = (min_x + max_x)/2
            center_y = (min_y + max_y)/2

            width = max_x - min_x 
            height = max_y - min_y 
            
            x = int(((center_x-min_x)/width)*250)
            y = int(((center_y-min_y)/height)*250)
            cv2.circle(whiteboardAdj,np.array([x,y],dtype= np.uint8),3,(0,255,0),1)
        
            cv2.circle(whiteboardAdj,np.array(self.PupilBuffor.getAvg(),dtype= np.uint8),3,(255,0,0),1)
            

            point = self.PupilBuffor.getAvg()
            x = int(((point[0])/30 - 3.5)*1920)
            y = int(((point[1])/30)*1080)
            self.red_dot_widget.move(x,y)
            print(f"move: {x,y} offset: {min_x,width}")
            
            vision_map_start = np.array((((landmarks[1,0]-min_x)/width)*250 + 15,0), dtype = np.uint8)
            vision_map_wh  = np.array((50,30), dtype = np.uint8)
            vision_map_end = vision_map_start+vision_map_wh

            # openness need to be calculated relatively to 250x250 frame
            print(f"openness of the eyes: {height} width: {width} scale: {height/width - 0.25}")
            # 0.40 > wide open
            # 0.30 > normally open - looking up or so
            # 0.20 > sligthly closed - looking down
            
            print(f"vision map: {vision_map_start} {vision_map_wh} {vision_map_end}")
            cv2.rectangle(whiteboardAdj,vision_map_start,vision_map_end,(255,0,0),1)

            self.pupilAdjLab.imshow(
                self.__convertFrame(whiteboardAdj))

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
    