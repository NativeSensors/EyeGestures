import numpy as np
from pynput import keyboard

from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QSizePolicy
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QImage, QPixmap, QBrush
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread

class DisplayWithMask(QWidget):
    def __init__(self, parent=None):
        super(Display, self).__init__(parent)
        self.label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def imshow(self, q_image):
        painter = QPainter(q_image)
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.green, Qt.DiagCrossPattern))
        painter.drawRect(100, 15, 400, 200)
        # Update the label's pixmap with the new frame
        pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap )
        self.label.repaint()
    
    def on_quit(self):
        self.close()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        super(Display, self).closeEvent(event)


class Display(QWidget):
    def __init__(self, parent=None):
        super(Display, self).__init__(parent)
        self.label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def imshow(self, q_image):
        pixmap = QPixmap.fromImage(q_image)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        # painter.setBrush(QBrush(Qt.green, Qt.DiagCrossPattern))
        painter.drawRect(100, 15, 400, 200)
        # Update the label's pixmap with the new frame
        self.label.setPixmap(pixmap)
        painter.end()
        
        self.label.repaint()
  
    def on_quit(self):
        self.close()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        super(Display, self).closeEvent(event)

class Worker(QObject):

    def __init__(self,thread):
        super().__init__()

        self.__displayPool = dict()
        self.__thread = thread
        
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

        self.__run = True

        self.thread = QThread()
        self.moveToThread(self.thread)

        self.thread.started.connect(self.run)
        self.thread.start()


    def imshow(self, name : str, frame: np.ndarray):
        if not name in self.__displayPool.keys():
            self.__displayPool[name] = Display()
            self.__displayPool[name].show()
        self.__displayPool[name].imshow(self.__convertFrame(frame))


    def on_quit(self,key):
        if not hasattr(key,'char'):
            return

        if key.char == 'q':
            self.__run = False

            for key in self.__displayPool.keys():
                self.__displayPool[key].on_quit()

            self.thread.quit()
            self.thread.wait()
            
    def __convertFrame(self,frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.rgbSwapped()
        return p

    def run(self):
        while self.__run:
            self.__thread()
