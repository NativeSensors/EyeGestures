import sys
import math
import random
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen
from PySide2.QtCore import Qt, QTimer, QPointF
import keyboard

from appUtils.dot import DotWidget

from pynput import keyboard

if __name__ == '__main__':
    app = QApplication(sys.argv)
    red_dot_widget = DotWidget(diameter=100,color = (255,120,0))
    red_dot_widget.show()
    red_dot_widget.move(100,100)
    blue_dot_widget = DotWidget(diameter=100,color = (120,120,255))
    blue_dot_widget.show()
    red_dot_widget.move(200,200)
    sys.exit(app.exec_())
