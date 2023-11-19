import math
import numpy as np

from eyeGestures.utils import VideoCapture, Buffor

from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QKeyEvent, QPainterPath, QPen, QImage, QPixmap
from PySide2.QtCore import Qt, QTimer, QPointF, QObject, QThread

class ScreenHist:

    def __init__(self,width,height,step):

        self.inc_step = 20

        self.step = step
        self.width = width
        self.height = height

        bars_x = int(self.width/self.step)
        bars_y = int(self.height/self.step)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

    def addPoint(self,point):

        self.axis_x[self.axis_x != 0] -= 1
        self.axis_y[self.axis_y != 0] -= 1

        (x,y) = point
        pos_x = int(x/self.step)
        pos_y = int(y/self.step)
        print(f"x: {x}, pos_x: {pos_x}")
        print(f"y: {y}, pos_y: {pos_y}")

        self.axis_x[pos_x] += self.inc_step
        self.axis_y[pos_y] += self.inc_step

        self.min_x = np.where(self.axis_x > self.inc_step*3)[0][0] * self.step
        self.max_x = np.where(self.axis_x > self.inc_step*3)[0][-1]* self.step
        self.min_y = np.where(self.axis_y > self.inc_step*3)[0][0] * self.step
        self.max_y = np.where(self.axis_y > self.inc_step*3)[0][-1]* self.step

        if not self.min_x is np.NAN:
            self.min_x = int(self.min_x)
        if not self.max_x is np.NAN:
            self.max_x = int(self.max_x)
        if not self.min_y is np.NAN:
            self.min_y = int(self.min_y)
        if not self.max_y is np.NAN:
            self.max_y = int(self.max_y)

    def getLims(self):
        return (self.min_x,self.max_x,self.min_y,self.max_y)

    def getCenter(self):
        return (
            int((self.max_x - self.min_x)/2 + self.min_x),
            int((self.max_y - self.min_y)/2 + self.min_y))

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)


class Screen:

    def __init__(self, screen_width = 0, screen_height = 0 , x = 0, y = 0, width = 0, height = 0):

        self.screen_buffor = Buffor(15)
        self.setWH(width,height)
        self.setCenter(x,y)

        self.screen_width  = screen_width
        self.screen_height = screen_height
        pass

    def getCenter(self):
        return (self.x,self.y)

    def getWH(self):
        return (self.width,self.height)

    def setCenter(self, x, y):
        self.x = x - int(self.width/2)
        self.y = y - int(self.height/2)

    def setWH(self, width, height):
        self.width = width
        self.height = height

    def convertToScreen(self, point):
        x = (point[0] - self.x) * ((point[0] - self.x) > 0)
        x = int((x/self.width) * self.screen_width)

        y = (point[1] - self.y) * ((point[1] - self.y) > 0)
        y = int((y/self.height) * self.screen_height)
        self.screen_buffor.add((x,y))

        return self.screen_buffor.getAvg()

    def getRect(self):
        return (self.x,self.y,self.width,self.height)
