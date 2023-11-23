from PySide2.QtWidgets import QApplication, QWidget, QLabel
from PySide2.QtGui import QPainter, QPixmap, QImage
from PySide2.QtCore import Qt, QPoint
import numpy as np
import cv2
import sys

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.startPoint = QPoint()
        self.currentPoint = QPoint()
        self.drawing = False
        self.image = np.zeros((280,170,3)) # Load your picture here
        
    def initUI(self):
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw Rectangle')
        self.label = QLabel(self)
        self.label.show()

    def mousePressEvent(self, event):
        self.drawing = True
        self.startPoint = event.pos()
        self.currentPoint = self.startPoint
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.currentPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        __start = np.array((self.startPoint.x(),self.startPoint.y()), dtype = np.uint32)
        __end   = np.array((self.currentPoint.x(),self.currentPoint.y()), dtype = np.uint32)
        print((__start),(__end))
        cv2.rectangle(self.image,(__start),(__start + __end),(255,0,0,255),3)
        self.drawing = False

    def __convertFrame(self,frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.rgbSwapped()
        return p

    def paintEvent(self, event):
        pixmap = QPixmap.fromImage(self.__convertFrame(self.image))
        self.label.setPixmap(pixmap )
        self.label.repaint()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CustomWidget()
    ex.show()
    sys.exit(app.exec_())
