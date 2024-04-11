import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import Qt, QRect
from PySide2.QtGui import QPainter

from ActivationZone import RoIMan

class RoiViewer(QWidget):
    def __init__(self):
        super().__init__()
        self._width = 300
        self._height = 200
        self.rectangles = dict()  # Define small rectangles as (x, y, width, height) tuples
        self.setMinimumSize(self.width,self.height)

    def add_rectangle(self, id, rectangle, display_width, display_height):
        x = rectangle[0] * self._width/display_width
        y = rectangle[1] * self._height/display_height
        width =  rectangle[2] * self.width/display_width
        height = rectangle[3] * self.height/display_height
        self.rectangles[id] = (x,y,width,height)

    def rm_rectangle(self, id):
        del self.rectangles[id]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother drawing

        # Draw rounded rectangle
        rounded_rect = self.rect()
        painter.setBrush(Qt.lightGray)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rounded_rect, 10, 10)

        # Draw small rectangles inside the rounded rectangle
        painter.setBrush(Qt.blue)
        for key in self.rectangles:
            rectangle = QRect(*self.rectangles[key])
            painter.drawRect(rectangle)

    def resizeEvent(self, event):
        # Update the width and height when the widget is resized
        self._width = event.size().width()
        self._height = event.size().height()
        super().resizeEvent(event)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = RoiViewer()
    widget.setWindowTitle('Custom Widget')
    widget.add_rectangle(0,(10,10,100,100),600,400)
    widget.add_rectangle(1,(120,10,300,300),600,400)
    widget.show()
    sys.exit(app.exec_())