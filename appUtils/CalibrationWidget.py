import sys
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt, QTimer, QRect
from PySide2.QtGui import QTransform
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from screeninfo import get_monitors

class WarningPill(QWidget):
    def __init__(self, position, text, angle = 0):
        super(WarningPill, self).__init__()
        
        width = 150
        height= 40

        # Set up the window attributes
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setGeometry(position[0], position[1], width, height)
        self.setStyleSheet("background-color: #99ffff00; border-radius: 10px;")

        # Add a label for displaying text
        self.angle = angle
        self.text = text
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, width, height)

    def disappear(self):
        self.hide()

    def show_again(self):
        self.setStyleSheet("background-color: #99ffff00; border-radius: 10px;")


class CalibrationWidget():
    def __init__(self):
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        # Create warning pills on each edge and add them to the layout
        self.warning_pills = [
            WarningPill((self.monitor.x + self.monitor.width/2 - 50,
                         self.monitor.y + 0), "Move cursor here", 0),
            WarningPill((self.monitor.x + self.monitor.width/2 - 50,
                         self.monitor.y + self.monitor.height - 50), "Move cursor here", 0),
            WarningPill((self.monitor.x + 0,
                         self.monitor.y + self.monitor.height/2), "Move cursor here", 90),
            WarningPill((self.monitor.x + self.monitor.width - 100,
                         self.monitor.y + self.monitor.height/2), "Move cursor here", -90)
        ]

        for pill in self.warning_pills:
            pill.show()

    def disappear(self):
        for pill in self.warning_pills:
            pill.disappear()

    def show_again(self):
        for pill in self.warning_pills:
            pill.show()
