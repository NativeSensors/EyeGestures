import math
import numpy as np

from scipy import signal

class Center():

    def __init__(self,x,y,width,height):
        self.x = (x + width)/2
        self.y = (y + height)/2

class Screen():

    def __init__(self,width,height):
        self.width = width
        self.height= height

    def getCenter(self):
        return Center(self.x,self.y,self.width, self.height)

class ScreenROI():

    def __init__(self,x,y,width,height):
        self.x = x 
        self.y = y
        self.width = width
        self.height= height

    def setCenter(self,x, y):
        self.x = x - self.width/2
        self.y = y - self.height/2

    def getCenter(self):
        return Center(self.x, self.y, self.width, self.height)
    
    def getBoundaries(self):
        return (self.x,self.y,self.width, self.height)


class Display():

    def __init__(self,width,height,offset_x,offset_y):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # self.buffor = Buffor(20)

    def getCenter(self):
        return self.__center
