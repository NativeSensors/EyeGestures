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

        self.min_x = self.__getParam((self.axis_x > self.inc_step*3),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*3),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*3),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*3),last=True)

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
        return (self.width,self.height)

    def setCenter(self, x, y):
        self.x = x - int(self.width/2)
        self.y = y - int(self.height/2)

    def scale(self,scale_w,scale_h, change = 5):
        
        diff_w = abs(self.old_scale_w - scale_w)
        diff_h = abs(self.old_scale_h - scale_h)
        
        if diff_w > change: 
            new_width  = int(self.width/self.old_scale_w * scale_w)
            self.old_scale_w = scale_w
            self.setWH(new_width,self.height)
        
        if diff_h > change: 
            new_height = int(self.height/self.old_scale_h * scale_h)
            self.old_scale_h = scale_h
            self.setWH(self.width,new_height)
            
        
    def scaleByStep(self,step_w=0.1,step_h=0.1):
        new_scale_w = float(self.old_scale_w) * (1 + step_w)
        new_scale_h = float(self.old_scale_h) * (1 + step_h)
        print(f"{new_scale_h} {float(self.old_scale_h)} {(1 + step_h)}")
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

        # print(f"x,y {x,y} lim: {self.x,self.y}")        
        return (x,y)

    def getRect(self):
        return (self.x,self.y,self.width,self.height)

class EdgeDetector:

    def __init__(self,width,height, x = 0,y = 0,w = 0,h = 0):

        self.width  = width
        self.height = height
        self.center_x = x + w/2
        self.center_y = y + h/2

        self.edge_max_x = int(self.center_x + w/2)
        self.edge_min_x = int(self.center_x - w/2)
        self.edge_max_y = int(self.center_y + h/2)
        self.edge_min_y = int(self.center_y - h/2)

        self.lim_max_x = 30
        self.lim_min_x = 30 
        self.lim_max_y = 30
        self.lim_min_y = 30 


    def setCenter(self,x,y):
        self.center_x = x 
        self.center_y = y

    def setLim(self,lim_min_x, lim_max_x, lim_min_y, lim_max_y):

        self.lim_max_x = lim_max_x
        self.lim_min_x = lim_min_x 
        self.lim_max_y = lim_max_y
        self.lim_min_y = lim_min_y 

    def __checkLims(self):

        if self.edge_max_x < self.lim_max_x - self.center_x:
            self.edge_max_x = self.lim_max_x - self.center_x

        if self.edge_min_x > self.center_x - self.lim_min_x:
            self.edge_min_x = self.center_x - self.lim_min_x
        
        if self.edge_max_y < self.lim_max_y - self.center_y:
            self.edge_max_y = self.lim_max_y - self.center_y

        if self.edge_min_y > self.center_y - self.lim_min_y:
            self.edge_min_y = self.center_y - self.lim_min_y
        
    def check(self, point_tracker, point_screen):
        (x_t,y_t) = point_tracker 
        (x_s,y_s) = point_screen

        # TODO: fix this to estimate w and h
        maring = 10
        if (x_s <= maring):
            self.edge_min_x = max(self.center_x - x_t, 0)
        elif (self.center_x - x_t > self.edge_min_x ) and (x_s > maring):
            self.edge_min_x = max(self.center_x - x_t, 0)

        if (x_s >= self.width - maring):
            self.edge_max_x = min(x_t - self.center_x, 500)
        elif (x_t - self.center_x > self.edge_max_x ) and (x_s < self.width - maring):
            self.edge_max_x = min(x_t - self.center_x, 500)
            
        if (y_s <= maring):
            self.edge_min_y = max(self.center_y - y_t, 0)
        elif (self.center_y - y_t > self.edge_min_y) and (y_s > maring):
            self.edge_min_y = max(self.center_x - y_t, 0)
        
        if (y_s >= self.height - maring):
            self.edge_max_y = min(y_t - self.center_y, 500)
        elif (y_t - self.center_y > self.edge_max_y) and (y_s < self.height - maring):
            self.edge_max_y = min(y_t - self.center_y, 500)

        self.__checkLims()
        
    def getBoundingBox(self):
        # print(self.center_x,self.center_y)
        w_l = int(self.center_x - self.edge_min_x) 
        w_r = int(self.center_x + self.edge_max_x)

        h_u = int(self.center_y - self.edge_min_y)
        h_d = int(self.center_y + self.edge_max_y) 
        
        return (w_l,h_u,w_r,h_d)

    def getCenter(self):
        w_l = self.center_x - self.edge_min_x
        w_r = self.center_x + self.edge_max_x

        h_u = self.center_y - self.edge_min_y
        h_d = self.center_y + self.edge_max_y 

        x = int((w_r + w_l)/2)
        y = int((h_u + h_d)/2)

        x = min(x,self.lim_max_x)
        x = max(x,self.lim_min_x)
        y = min(y,self.lim_max_y)
        y = max(y,self.lim_min_y)
    
        return (x, y)

class ScreenManager:

    def __init__(self,eye_screen_w,eye_screen_h):

        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h
        self.step         = 10 
        self.eyeScreen    = Screen(1920,1080,190,60,int(1920/50),int(1080/50))
        self.eyeHist      = ScreenHist(self.eye_screen_w,self.eye_screen_h,self.step)
        self.edgeDetector = EdgeDetector(1920,1080, 250,250,10,10)
        self.pointsBuffor = Buffor(50)
        pass

    def process(self, eye ,point : (int,int)):
        assert(np.array(point).shape[0] == 2)

        self.eyeHist.addPoint(point)
        (x,y) = self.eyeHist.getCenter()
        (lim_min_x,lim_max_x,lim_min_y,lim_max_y) = self.eyeHist.getLims()
        
        # (lim_min_x,lim_max_x,lim_min_y,lim_max_y) = (x-30,x+30,y-30,y+30)
        # =====================================
        # ---------histogram obtained---------- 
        # =====================================
        
        point = self.eyeScreen.limitToScreen(point)
        self.pointsBuffor.add(point)

        self.eyeScreen.setCenter(x,y) 
        w1,h1 = self.eyeScreen.getWH()
        
        (w_hist,h_hist) = (lim_max_x - lim_min_x,lim_max_y - lim_min_y)

        if(w_hist > w1):
            self.eyeScreen.scaleByStep(0.1,0.0)
        
        if(h_hist > h1):
            self.eyeScreen.scaleByStep(0.0,0.1)

        # =====================================
        # if screen is bigger than edges make it smaller
        # =====================================
        self.edgeDetector.setCenter(x,y)
        self.edgeDetector.setLim(lim_min_x,lim_max_x,lim_min_y,lim_max_y)

        w_l,h_u,w_r,h_d = self.edgeDetector.getBoundingBox()
        w = w_r - w_l 
        h = h_d - h_u  
        print(w, w1)
        if (w < w1):
            self.eyeScreen.scaleByStep(-0.1,0.0)
        
        if (h < h1):
            self.eyeScreen.scaleByStep(0.0,-0.1)
        
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