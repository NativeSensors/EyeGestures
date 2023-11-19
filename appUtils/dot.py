import sys
import math
import random
from PySide2.QtWidgets import QApplication, QWidget, QLabel
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen
from PySide2.QtCore import Qt, QTimer, QPointF

from pynput import keyboard

class DotWidget(QWidget):
    
    def __init__(self, diameter=20, color=(255,255,255)):
        super().__init__()
        self.outer_radius = diameter / 4
        self.inner_radii = [self.outer_radius * 0.7, self.outer_radius * 0.8, self.outer_radius * 0.7, self.outer_radius * 0.3]  # Different sizes for inner circles
        self.orbit_distances = [self.outer_radius * 0.2, self.outer_radius * 0.2, self.outer_radius * 0.2, self.outer_radius * 0.2]  # Distances from center
        self.angles = [0, 120, 240, 150]  # Starting angles for the inner circles

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(diameter, diameter)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_orbits)        
        self.timer.start(10)  # Update the orbits every 50 milliseconds

        self.color = color

        self.position_label = QLabel(self)
        
        self.move(500,500)
        
        # Start listening for the 'q' key press in the background
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()

    def moveEvent(self, event):
        self.update_position_label()  # Update the position label when the widget is moved
        super().moveEvent(event)

    def update_position_label(self):
        x, y = self.pos().x(), self.pos().y()
        self.position_label.setText(f'{x},{y}') 

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

        # Draw the large red circle
        R,G,B= self.color
        painter.setBrush(QColor(R,G,B, 100))
        painter.setPen(QColor(R,G,B, 0))
        
        # Draw the smaller orbiting circles
        for n, (radius, distance, angle) in enumerate(zip(self.inner_radii, self.orbit_distances, self.angles)):
            if self.orbit_distances[n] >= (self.outer_radius/4 - (radius * random.random())):
                self.orbit_distances[n] -= random.random()
            else:
                self.orbit_distances[n] += random.random() 

            rad_angle = math.radians(angle)
            center_x = self.rect().center().x() + distance * math.cos(rad_angle)
            center_y = self.rect().center().y() + distance * math.sin(rad_angle)

            path.addEllipse(QPointF(center_x, center_y), radius, radius)
            
        painter.drawPath(path)


    def on_quit(self,key):
        print(dir(key))
        if key.char == 'q':
            # Stop listening to the keyboard input and close the application
            self.close()

    def closeEvent(self, event):
        # Ensure the application quits completely
        QApplication.quit()


    def showEvent(self, event):
        self.setFocus()  # Set focus to the widget when it is shown
