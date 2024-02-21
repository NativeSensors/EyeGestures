import sys
import math
import random
from PySide2.QtWidgets import QApplication, QWidget, QLabel
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QRadialGradient, QBrush
from PySide2.QtCore import Qt, QTimer, QPointF

from pynput import keyboard

class DotWidget(QWidget):

    def __init__(self, diameter=20, color=(255,255,255)):
        super().__init__()
        self.outer_radius = diameter / 2
        self.inner_radii = [self.outer_radius * 0.7, self.outer_radius * 0.8, self.outer_radius * 0.7, self.outer_radius * 0.3]  # Different sizes for inner circles
        self.orbit_distances = [self.outer_radius * 0.0, self.outer_radius * 0.0, self.outer_radius * 0.0, self.outer_radius * 0.0]  # Distances from center
        self.angles = [0, 120, 240, 150]  # Starting angles for the inner circles

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(diameter, diameter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_orbits)
        self.timer.start(10)  # Update the orbits every 50 milliseconds

        self.color = color

        self.move(500,500)

    def moveEvent(self, event):
        super().moveEvent(event)

    def update_orbits(self):
        self.angles = [(angle + 2 * random.random()*2) % 360 for angle in self.angles]  # Increment the angles
        self.repaint()  # Trigger a repaint to update the positions

    def update_blob(self):
        self.repaint()  # Trigger a repaint to draw a new blob

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)

        # Draw the large semitransparent circle with a white thick border
        R, G, B = self.color
        outer_circle_radius = self.outer_radius/2
        outer_circle_center = self.rect().center()

        gradient = QRadialGradient(outer_circle_center, outer_circle_radius)
        gradient.setColorAt(0, QColor(205, 255, 255, 50))  # Semitransparent at center
        gradient.setColorAt(1, QColor(205, 255, 255, 50))  # Semitransparent at edges

        # Set the brush to the radial gradient
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(205, 255, 255), 2))  # White thick border

        path.addEllipse(outer_circle_center, outer_circle_radius, outer_circle_radius)
        painter.drawPath(path)
    
    def close_event(self):
        self.timer.stop()
        self.close() 

    def on_quit(self,key):
        # Stop listening to the keyboard input and close the application
        self.close()

    def closeEvent(self, event):
        # Stop the frame processor when closing the widget
        super(DotWidget, self).closeEvent(event)

    def showEvent(self, event):
        self.setFocus()  # Set focus to the widget when it is shown

    def setColour(self,color):
        self.color = color
