import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import Qt

class RedDotWidget(QWidget):
    def __init__(self, position,diameter=50):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.x = position[0]
        self.y = position[1]
        self.move(self.x, self.y) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.diameter, self.diameter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    red_dot_widget = RedDotWidget([100,100])
    red_dot_widget.show()
    sys.exit(app.exec_())