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
            self.listener.join()
            self.close()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        self.frame_processor.stop()
        self.frame_processor.wait()
        super(Display, self).closeEvent(event)


class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.frameDisplay = Display()  
        self.pupilLab     = Display()
        self.frameDisplay.show()
        self.pupilLab.show()
        
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
            self.listener.join()
            self.close()

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
            
            try:
                face = self.gestures.getFeatures(frame)

                print(face)
                self.frameDisplay.imshow(
                    self.__convertFrame(frame))

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
                    height = max_y - min_y 

                    x = int(((center_x-min_x)/width)*250)
                    y = int(((center_y-min_y)/height)*250)
                    cv2.circle(whiteboard,np.array([x,y],dtype= np.uint8),3,(0,255,0),1)
                    

                    print(f"width,height {width,height}")
                    print(f"pupil {pupil}")
                    point = pupil[0]
                    x = int(((point[0]-min_x)/width)*250)
                    y = int(((point[1]-min_y)/height)*250)
                    cv2.circle(whiteboard,np.array([x,y],dtype= np.uint8),3,(255,0,0),1)
                    print(f"x,y: {x,y}")

                    for point in landmarks:
                        x = int(((point[0]-min_x)/width) * 250)
                        y = int(((point[1]-min_y)/height) * 250)
                        print(f"x,y: {x,y}")
                        cv2.circle(whiteboard,np.array([x,y],dtype= np.uint8),3,(0,0,255),1)

                    self.pupilLab.imshow(
                        self.__convertFrame(whiteboard))
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
    