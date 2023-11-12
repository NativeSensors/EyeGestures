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


class NoseDirection:

    def __init__(self):
        self.__tmp__buffor = Buffor(5)
        self.__tmp__mapped_nose_buffor = Buffor(20)
        self.min_nose_x = 1.0
        self.min_nose_y = 1.0
        self.max_nose_x = 0.0
        self.max_nose_y = 0.0
        self.min_mapped_nose_x = 1.0
        self.min_mapped_nose_y = 1.0
        self.max_mapped_nose_x = 0.0
        self.max_mapped_nose_y = 0.0
        
    def __set_lim_nose(self,avg):
        (avg_nose_x,avg_nose_y) = avg
        self.min_nose_x = avg_nose_x if avg_nose_x < self.min_nose_x else self.min_nose_x
        self.min_nose_y = avg_nose_y if avg_nose_y < self.min_nose_y else self.min_nose_y
        self.max_nose_x = avg_nose_x if avg_nose_x > self.max_nose_x else self.max_nose_x
        self.max_nose_y = avg_nose_y if avg_nose_y > self.max_nose_y else self.max_nose_y
        print(f"nose: max: {self.max_nose_x,self.max_nose_y} min: {self.min_nose_x,self.min_nose_y}")        
    
    def __get_mapped_nose(self,avg_nose):
        (avg_nose_x,avg_nose_y) = avg_nose
        return (avg_nose_x/(self.max_nose_x - self.min_nose_x),
                    avg_nose_y/(self.max_nose_y - self.min_nose_y))

    def __set_lim_mapped(self,mapped_nose):
        self.min_mapped_nose_x = mapped_nose[0] if mapped_nose[0] < self.min_mapped_nose_x else self.min_mapped_nose_x
        self.min_mapped_nose_y = mapped_nose[1] if mapped_nose[1] < self.min_mapped_nose_y else self.min_mapped_nose_y
        self.max_mapped_nose_x = mapped_nose[0] if (mapped_nose[0] > self.max_mapped_nose_x) and (mapped_nose[0] < 1.2) else self.max_mapped_nose_x
        self.max_mapped_nose_y = mapped_nose[1] if (mapped_nose[1] > self.max_mapped_nose_y) and (mapped_nose[1] < 1.2) else self.max_mapped_nose_y
        

    def getPos(self,nose):
        nose_center = nose.getcenterDist()
            
        self.__tmp__buffor.add(nose_center)

        avg_nose = self.__tmp__buffor.getAvg()
        if self.__tmp__buffor.getLen() >= 5:
            self.__set_lim_nose(avg_nose)
            
            mapped_nose = self.__get_mapped_nose(avg_nose)
            self.__tmp__mapped_nose_buffor.add(mapped_nose)
            if self.__tmp__mapped_nose_buffor.getLen() >= 20:
                self.__set_lim_mapped(mapped_nose)
                print(f"dnose: {mapped_nose[0]-self.min_mapped_nose_x,mapped_nose[1]-self.min_mapped_nose_y}")
                return np.array([mapped_nose[0] - self.min_mapped_nose_x, mapped_nose[1]-self.min_mapped_nose_y])
                
                # print(f"dnose: max: {self.max_dnose_x,self.max_dnose_y} min: {self.min_dnose_x,self.min_dnose_y}")
        return np.full((1,2),np.NAN)
            

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
        
        self.dirNose = NoseDirection()
        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')

        self.PupilBuffor = Buffor(10)

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
            pupil = face.getLeftPupil()
            landmarks = face.getLeftEye()
            
            # display debug data:
            whiteboard = np.full((250,250,3),255.0,dtype = np.uint8)
            
            # get center: 
            min_x = np.min(landmarks[:,0])
            max_x = np.max(landmarks[:,0])
            min_y = np.min(landmarks[:,1])
            max_y = np.max(landmarks[:,1])

            center_x = (min_x + max_x)/2
            center_y = (min_y + max_y)/2

            width = max_x - min_x 
            # height = max_y - min_y 
            height = 20

            x = int(((center_x-min_x)/width)*250)
            y = int(((center_y-min_y)/height)*250)
            cv2.circle(whiteboard,np.array([x,y],dtype= np.uint8),3,(0,255,0),1)
            

            print(f"width,height {width,height}")
            print(f"pupil {pupil}")
            point = pupil[0]
            x = int(((point[0]-min_x)/width)*250)
            y = int(((point[1]-min_y)/height)*250)
            self.PupilBuffor.add((x,y))
            print(self.PupilBuffor)
            cv2.circle(whiteboard,np.array(self.PupilBuffor.getAvg(),dtype= np.uint8),3,(255,0,0),1)
            print(f"x,y: {self.PupilBuffor.getAvg()}")

            for point in landmarks:
                x = int(((point[0]-min_x)/width) * 250)
                y = int(((point[1]-min_y)/height) * 250)
                print(f"x,y: {x,y}")
                cv2.circle(whiteboard,np.array([x,y],dtype= np.uint8),3,(0,0,255),1)

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
        
            point = self.PupilBuffor.getAvg()
            x = int(((point[0]-min_x)/width)*250)
            y = int(((point[1]-min_y)/height)*250)
            cv2.circle(whiteboardAdj,np.array(point,dtype= np.uint8),3,(255,0,0),1)
            
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

            self.dirNose.getPos(face.getNoseFeatures())
            
            
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
    