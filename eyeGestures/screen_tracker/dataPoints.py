import math
import numpy as np

from eyeGestures.utils import Buffor

from scipy import signal

class Center():

    def __init__(self,x,y,width,height):
        self.x = (x + width)/2
        self.y = (y + height)/2

class Screen():

    def __init__(self,x,y,width,height):
        self.x = x 
        self.y = y
        self.width = width
        self.height= height
        self.buffor = Buffor(20)

    def getCenter(self):
        return Center(self.x, self.y, self.width, self.height)


class ScreenROI():

    def __init__(self,x,y,width,height):
        self.x = x 
        self.y = y
        self.width = width
        self.height= height
        self.buffor = Buffor(20)

    def getCenter(self):
        return Center(self.x, self.y, self.width, self.height)

class Display():

    def __init__(self,width,height,offset_x,offset_y):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # self.buffor = Buffor(20)

    def getCenter(self):
        return self.__center

class DataPoint():

    def __init__(self,
                screen_w,
                screen_h,
                display_w,
                display_h,
                display_offset_w,
                display_offset_h):
        
        self.buffor  = Buffor(50)

        self.screen  = dataScreen(
            0,
            0,
            screen_w,
            screen_h
        )
        self.display = DataDisplay(
            display_w,
            display_h,
            display_offset_w,
            display_offset_h
        )

    def getScreen(self):
        return self.screen 

    def getDisplay(self):
        return self.display 
    
    def getHeatMap(self):
        return Heatmap(
            self.screen.width,
            self.screen.height,
            self.buffor)
    
    def add(self,point):
        self.buffor.add(point)

    def getLatest(self):
        return self.buffor.getLast()