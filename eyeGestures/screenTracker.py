import math
import numpy as np

from screeninfo import get_monitors
from eyeGestures.utils import Buffor

from scipy import signal

class ScreenHist:

    def __init__(self,width,height,step):
        self.inc_step = 10

        self.step = step
        self.width = width
        self.height = height

        bars_x = int(self.width/self.step)
        bars_y = int(self.height/self.step)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

        self.confidence_limit   = 1000
        self.total_points       = 0

        self.fading = 1

    def __getParam(self,param,last : bool = False):
        ret = 0
        retArray = np.where(param)
        
        if len(retArray[0]) > 0:
            ret = retArray[0][- int(last)] * self.step

            if not ret == np.NAN:
                ret = int(ret)
        
        return ret
        
    def addPoint(self,point):
        self.total_points += 1
        
        self.axis_x[self.axis_x > 0] -= self.fading
        self.axis_y[self.axis_y > 0] -= self.fading
        self.axis_x[self.axis_x < 0] = 0
        self.axis_y[self.axis_y < 0] = 0
        
        (x,y) = point
        pos_x = int(x/self.step)
        pos_y = int(y/self.step)
        
        self.axis_x[pos_x] += self.inc_step
        self.axis_y[pos_y] += self.inc_step

        self.min_x = self.__getParam((self.axis_x > self.inc_step*5),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*5),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*5),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*5),last=True)

    def setFading(self,fading : int):
        self.fading = fading

    def getLims(self):
        return (self.min_x,self.max_x,self.min_y,self.max_y)

    def getCenter(self):

        self.center_x = int((self.max_x - self.min_x)/2 + self.min_x)
        self.center_y = int((self.max_y - self.min_y)/2 + self.min_y)

        return (self.center_x,self.center_y)

    def confident(self):
        return self.total_points > self.confidence_limit

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)

class Screen:

    def __init__(self, screen_width = 0, screen_height = 0 , x = 0, y = 0, width = 0, height = 0):
        self.old_scale_w = 1.0
        self.old_scale_h = 1.0

        self.screen_buffor = Buffor(15)
        self.setWH(width,height)
        self.setCenter(x,y)

        self.screen_width  = screen_width
        self.screen_height = screen_height
        pass

    def getCenter(self):
        return (self.x,self.y)

    def setWH(self, width, height):
        self.width  = width
        self.height = height

    def getWH(self):
        return (int(self.width),int(self.height))

    def setCenter(self, x, y):
        self.x = x - int(self.width/2)
        self.y = y - int(self.height/2)

    def scale(self,scale_w,scale_h, change = 0.5):
        
        diff_w = abs(self.old_scale_w - scale_w)
        diff_h = abs(self.old_scale_h - scale_h)
        
        if diff_w > change: 
            new_width  = self.width/self.old_scale_w * scale_w
            self.old_scale_w = scale_w
            self.setWH(new_width,self.width)
        
        if diff_h > change: 
            new_height = self.height/self.old_scale_h * scale_h
            self.old_scale_h = scale_h
            self.setWH(self.width,new_height)    
        
    def scaleByStep(self,step_w=0.1,step_h=0.1):
        self.old_scale_w = 1.0
        self.old_scale_h = 1.0
        new_scale_w = float(self.old_scale_w + step_w)
        new_scale_h = float(self.old_scale_h + step_h)
        self.scale(new_scale_w,new_scale_h,0)

    def convertToScreen(self, point):
        x = (point[0] - self.x) * ((point[0] - self.x) > 0)
        x = int((x/self.width) * self.screen_width)

        y = (point[1] - self.y) * ((point[1] - self.y) > 0)
        y = int((y/self.height) * self.screen_height)

        x = max(x,0)
        y = max(y,0)
        x = min(x,self.screen_width)
        y = min(y,self.screen_height)

        self.screen_buffor.add((x,y))
        return self.screen_buffor.getAvg()
    
    def limitToScreen(self, point):
        margin = 10
        x = max(int(self.x - margin),int(point[0]))
        y = max(int(self.y - margin),int(point[1]))
        
        x = min(int(self.x + self.width  + margin),x)
        y = min(int(self.y + self.height + margin),y)

        return (x,y)

    def getRect(self):
        return (int(self.x),int(self.y),int(self.width),int(self.height))

class EdgeDetector:

    def __init__(self,width,height, x = 0,y = 0,w = 500,h = 500):

        self.width  = width
        self.height = height
        
        self.w = w
        self.h = h
        self.center_x = x + w/2
        self.center_y = y + h/2

        self.edge_max_x = int(self.center_x + w/2)
        self.edge_min_x = int(self.center_x - w/2)
        self.edge_max_y = int(self.center_y + h/2)
        self.edge_min_y = int(self.center_y - h/2)

    def setCenter(self,x,y):
        self.center_x = x 
        self.center_y = y

    def setLim(self,lim_min_x, lim_max_x, lim_min_y, lim_max_y):

        self.lim_max_x = lim_max_x
        self.lim_min_x = lim_min_x 
        self.lim_max_y = lim_max_y
        self.lim_min_y = lim_min_y 

    def check(self, point_tracker, point_screen):
        (x_t,y_t) = point_tracker 
        (x_s,y_s) = point_screen

        # TODO: fix this to estimate w and h
        if(x_s <= 0 or x_s >= self.width):
            self.w = abs(self.center_x - x_t) * 2 + 1
        
        if(y_s <= 0 or y_s >= self.height):
            self.h = abs(self.center_y - y_t) * 2 + 1
                
    def getBoundingBox(self):
        x = int(self.center_x - self.w/2)
        y = int(self.center_y - self.h/2)
        
        return (x,y,int(self.w),int(self.h))

    def getCenter(self):    
        return (self.center_x, self.center_y)

class ScreenManager:

    def __init__(self,eye_screen_w,eye_screen_h):

        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h
        self.step         = 10 
        self.eyeScreen    = Screen(self.monitor.width,
                                   self.monitor.height,
                                   190,60,
                                   int(self.monitor.width/50),
                                   int(self.monitor.height/50))

        self.eyeHist      = ScreenHist(self.monitor.width,
                                       self.monitor.height,
                                       self.step)
    
        self.edgeDetector = EdgeDetector(self.monitor.width,
                                         self.monitor.height,
                                         250,250,
                                         10,10)
        self.pointsBuffor  = Buffor(50)
        self.limsWHBuffor  = Buffor(20)
        self.edgesWHBuffor = Buffor(20)
        

    def __scale_up_to_hist(self,width,height):
        (lim_min_x,lim_max_x,lim_min_y,lim_max_y) = self.eyeHist.getLims()

        (w_hist,h_hist) = (lim_max_x - lim_min_x,lim_max_y - lim_min_y)

        self.limsWHBuffor.add((w_hist,h_hist))
        (w_hist,h_hist) = self.limsWHBuffor.getAvg()

        if(w_hist > width):
            self.eyeScreen.scaleByStep(0.1,0.0)
        
        if(h_hist > height):
            self.eyeScreen.scaleByStep(0.0,0.1)


    def __scale_down_to_edge(self,width,height):
        _,_,w,h = self.edgeDetector.getBoundingBox()
        
        self.edgesWHBuffor.add((w,h))
        (w,h) = self.edgesWHBuffor.getAvg()

        if (w < width):
            self.eyeScreen.scaleByStep(-0.1,0.0)
        
        if (h < height):
            self.eyeScreen.scaleByStep(0.0,-0.1)


    def process(self, point : (int,int)):
        assert(np.array(point).shape[0] == 2)

        self.eyeHist.addPoint(point)
        (x,y) = self.eyeHist.getCenter()
        
        # =====================================
        # ---------histogram obtained---------- 
        # =====================================

        point = self.eyeScreen.limitToScreen(point)
        self.pointsBuffor.add(point)

        self.eyeScreen.setCenter(x,y) 
        
        w1,h1 = self.eyeScreen.getWH()
        self.__scale_up_to_hist(w1,h1)

        # =====================================
        # if screen is bigger than edges make it smaller
        # =====================================
        
        self.edgeDetector.setCenter(x,y)
        self.__scale_down_to_edge(w1,h1)

        (lim_min_x,lim_max_x,lim_min_y,lim_max_y) = self.eyeHist.getLims()
        self.edgeDetector.setLim(lim_min_x,lim_max_x,lim_min_y,lim_max_y)
        
        # ====================================
        p = self.eyeScreen.convertToScreen(point)
        
        if self.pointsBuffor.getLen() > 20:
            self.edgeDetector.check(point,p)
            
        p += (self.monitor.x,self.monitor.y)

        return p

    def getScreen(self):
        return self.eyeScreen

    def getHist(self):
        return self.eyeHist
    
    def getPointsHistory(self):
        return self.pointsBuffor.getBuffor()

    def getEdgeDetector(self):
        return self.edgeDetector