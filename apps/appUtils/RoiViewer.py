import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import Qt, QRect
from PySide2.QtGui import QPainter, QColor

class RoiViewer(QWidget):
    def __init__(self):
        super().__init__()
        self._width = 300
        self._height = 200
        self.rectangles = dict()  # Define small rectangles as (x, y, width, height) tuples
        self.dots = dict()
        self.setMinimumSize(self.width,self.height)

    def add_rectangle(self, id, rectangle, display_width, display_height, color="#0600c2"):
        x = rectangle[0] * self._width/display_width
        y = rectangle[1] * self._height/display_height
        width =  rectangle[2] * self.width/display_width
        height = rectangle[3] * self.height/display_height
        self.rectangles[id] = [color,(x,y,width,height)]

    def update_rectangle_color(self, id, color="#0600c2"):
        self.rectangles[id][0] = color

    def add_dot(self, id, rectangle, display_width, display_height):
        x = rectangle[0] * self._width/display_width
        y = rectangle[1] * self._height/display_height
        self.dots[id] = (x,y,10,10)

    def rm_rectangle(self, id):
        del self.rectangles[id]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother drawing

        # Draw rounded rectangle
        rounded_rect = self.rect()
        painter.setBrush(QColor("#020024"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rounded_rect, 10, 10)

        # Draw small rectangles inside the rounded rectangle
        for key in self.rectangles:
            color = self.rectangles[key][0]
            rect = self.rectangles[key][1]
            painter.setBrush(QColor(color))
            rectangle = QRect(*rect)
            painter.drawRoundedRect(rectangle, 10, 10)

        painter.setBrush(QColor("#c03dff"))
        for key in self.dots:
            rectangle = QRect(*self.dots[key])
            painter.drawRoundedRect(rectangle, 10, 10)

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