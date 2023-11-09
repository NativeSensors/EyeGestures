import sys
import math
import random
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread
import keyboard

from eyeGestures.utils import VideoCapture

from eyeGestures.eyegestures import EyeGestures
from screeninfo import get_monitors

from appUtils.dot import DotWidget

# def main_thread(blue_dot,red_dot,eyeGestures):
#     app = QApplication(sys.argv)

#     cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
#     monitors = get_monitors()
    
#     (width,height) = (int(monitors[0].width),int(monitors[0].height))
    
#     ret = True
#     while ret:    
#         ret, frame = cap.read()
        
#         if not gestures.isCalibrated():
#             cPoint = gestures.calibrate(frame)
#             ePoint = gestures.estimate(frame)     
        
#             x = int(cPoint[0]*width)
#             y = int(cPoint[1]*height)
#             red_dot.move(x,y,(255,0,0))
            
#         else:
#             ePoint = gestures.estimate(frame)     


#         if not np.isnan(ePoint).any():
#             x = int(ePoint[0]*width)
#             y = int(ePoint[1]*height)
#             blue_dot.move(x,y,(255,0,0))
        
#         if cv2.waitKey(1) == ord('q'):
#             pass


#     #show point on sandbox
#     cv2.destroyAllWindows()


class Worker(QObject):

    def __init__(self):
        super().__init__()

        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        self.gestures = EyeGestures(height,width)

        self.red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
        self.blue_dot_widget = DotWidget(diameter=100,color = (120,120,255))

        self.red_dot_widget.move(2432,1368)

        self.red_dot_widget.show()
        self.blue_dot_widget.show()
        
        self.cap = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')

        
    def run(self):
        monitors = get_monitors()
        (width,height) = (int(monitors[0].width),int(monitors[0].height))
        print("starting thread")
        ret = True
        while ret:

            print(f"looping {ret}")
            ret, frame = self.cap.read()

            print("received frame")
            if not self.gestures.isCalibrated():
                cPoint = self.gestures.calibrate(frame)
                print(f"cPoint: {cPoint}")
                ePoint = self.gestures.estimate(frame)     
                print(f"ePoint: {ePoint}")
                
                x = int(cPoint[0]*width)
                y = int(cPoint[1]*height)
                print(x,y)
                self.red_dot_widget.move(x,y)
                
            else:
                ePoint = self.gestures.estimate(frame)     


            if not np.isnan(ePoint).any():
                x = int(ePoint[0]*width)
                y = int(ePoint[1]*height)
                self.blue_dot_widget.move(x,y)
            
            if cv2.waitKey(1) == ord('q'):
                pass


        #show point on sandbox
        cv2.destroyAllWindows()

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.thread = QThread()
#         self.worker = Worker()
#         self.worker.moveToThread(self.thread)

#         # Connect signals
#         # self.worker.finished.connect(self.thread.quit)
#         # self.worker.progress.connect(self.update_progress)  # If you want to update the GUI
#         # self.thread.started.connect(self.worker.run)

#         # # Clean up
#         # self.thread.finished.connect(self.thread.deleteLater)

#         # # Start the thread
#         # self.thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread = QThread()
    worker = Worker()
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    thread.start()

    sys.exit(app.exec_())
    