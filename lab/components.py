import math
import numpy as np

from screeninfo import get_monitors
from eyeGestures.utils import Buffor

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class ScreenFinder:
    
    def __init__(self):
        pass

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

        self.confidence_limit   = 300 
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
        print(f"self.total_points: {self.total_points}")

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
        
        if self.total_points < self.confidence_limit:
            self.center_x = int((self.max_x - self.min_x)/2 + self.min_x)
            self.center_y = int((self.max_y - self.min_y)/2 + self.min_y)

        return (self.center_x,self.center_y)

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
        self.width = width
        self.height = height

    def getWH(self):
        return (self.width,self.height)

    def setCenter(self, x, y):
        self.x = x - int(self.width/2)
        self.y = y - int(self.height/2)

    def scale(self,scale_w,scale_h, change = 5):
        if self.old_scale_w == 0 or self.old_scale_h == 0:
            self.old_scale_w = scale_w
            self.old_scale_h = scale_h
        else:
            diff = abs(self.old_scale_w - scale_w)
            if diff > change: 
                width  = int(self.width/self.old_scale_w * scale_w)
                height = int(self.height/self.old_scale_h * scale_h)
                self.old_scale_w = scale_w
                self.old_scale_h = scale_h
                self.setWH(width,height)
                return diff

        return 0

    def scaleByStep(self,step_W=0.1,step_h=0.1):
        new_scale_w = float(self.old_scale_w) * (1 + step_W)
        new_scale_h = float(self.old_scale_h) * (1 + step_h)
        self.scale(new_scale_w,new_scale_h,0)

    def convertToScreen(self, point):
        x = (point[0] - self.x) * ((point[0] - self.x) > 0)
        x = int((x/self.width) * self.screen_width)

        y = (point[1] - self.y) * ((point[1] - self.y) > 0)
        y = int((y/self.height) * self.screen_height)
        self.screen_buffor.add((x,y))

        return self.screen_buffor.getAvg()

    def getRect(self):
        return (self.x,self.y,self.width,self.height)

class EdgeDetector:

    def __init__(self,width,height, x = 0,y = 0,w = 0,h = 0):

        self.width  = width
        self.height = height
        self.center_x = 0 
        self.center_y = 0

        self.edge_max_x = x + w
        self.edge_min_x = x 
        self.edge_max_y = y + h
        self.edge_min_y = y 

        self.lim_max_x = 0
        self.lim_min_x = 0 
        self.lim_max_y = 0
        self.lim_min_y = 0 


    def setCenter(self,x,y):
        self.center_x = x 
        self.center_y = y

    def setLim(self,lim_min_x, lim_max_x, lim_min_y, lim_max_y):

        self.lim_max_x = lim_max_x
        self.lim_min_x = lim_min_x 
        self.lim_max_y = lim_max_y
        self.lim_min_y = lim_min_y 

    def __checkLims(self):

        if self.edge_max_x < self.lim_max_x:
            self.edge_max_x = self.lim_max_x

        if self.edge_min_x > self.lim_min_x:
            self.edge_min_x = self.lim_min_x
        
        if self.edge_max_y < self.lim_max_y:
            self.edge_max_y = self.lim_max_y

        if self.edge_min_y > self.lim_min_y:
            self.edge_min_y = self.lim_min_y
        
    def check(self, point_tracker, point_screen):
        (x_t,y_t) = point_tracker 
        (x_s,y_s) = point_screen

        maring = 0
        if (x_s <= maring):
            self.edge_min_x = x_t
        # elif (x_t < self.edge_min_x):
        #     self.edge_min_x = x_t

        if (x_s >= self.width - maring):
            self.edge_max_x = x_t
        # elif (x_t > self.edge_max_x):
        #     self.edge_max_x = x_t

        if (y_s <= maring):
            self.edge_min_y = y_t
        # elif (y_t < self.edge_min_y):
        #     self.edge_min_y = y_t
        
        if (y_s >= self.height - maring):
            self.edge_max_y = y_t
        # elif (y_t > self.edge_max_y):
        #     self.edge_max_y = y_t

        self.__checkLims()

    def getBoundingBox(self):
        w   = int((self.edge_max_x - self.edge_min_x))
        h   = int((self.edge_max_y - self.edge_min_y))
        x,y = int(self.edge_min_x),int(self.edge_min_y)
        return (x,y,w,h)

class ScreenManager:

    def __init__(self,eye_screen_w,eye_screen_h):

        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h
        self.step         = 10 
        self.eyeScreen    = Screen(1920,1080,190,60,int(1920/10),int(1080/10))
        self.eyeHist      = ScreenHist(self.eye_screen_w,self.eye_screen_h,self.step)
        self.edgeDetector = EdgeDetector(1920,1080, 250,250,10,10)
        self.pointsBuffor = Buffor(50)
        pass

    def process(self, eye ,point : (int,int)):
        assert(np.array(point).shape[0] == 2)

        self.pointsBuffor.add(point)
        self.eyeHist.addPoint(point)
        (x,y) = self.eyeHist.getCenter()
        
        (lim_min_x,lim_max_x,lim_min_y,lim_max_y) = self.eyeHist.getLims()
    
        self.edgeDetector.setLim(lim_min_x,lim_max_x,lim_min_y,lim_max_y)
        self.edgeDetector.setCenter(x,y)
        self.eyeScreen.setCenter(x,y)


        _,_,w,h = self.edgeDetector.getBoundingBox()
        w1,h1   = self.eyeScreen.getWH()

        if (w - w1) < 0.5 and (h - h1) < 0.5:
            print(w-w1,h-h1)
            step_sign_w = np.sign(w - w1) 
            step_sign_h = np.sign(h - h1) 

            self.eyeScreen.scaleByStep(0.1*step_sign_w,0.1*step_sign_h)
        
        if w1 < (lim_max_x - lim_min_x) or h1 < (lim_max_y - lim_min_y):
            self.eyeScreen.setWH((lim_max_x - lim_min_x),(lim_max_y - lim_min_y))
        # elif (w - w1 - 10) > 0.5 or (h - h1 - 10) > 0.5:
        #     self.eyeScreen.setWH(w-10,h-10)
        # scale_w = (eye.width  + eye.width)/2
        # scale_h = (eye.height + eye.height)/2

        # change = self.eyeScreen.scale(scale_w, scale_w)

        # if change > 10:
        #     self.eyeHist.setFading(500)
        # else:
        #     self.eyeHist.setFading(1)

        min_x,max_x,min_y,max_y = self.eyeHist.getLims()

        # if not np.array([min_x,max_x,min_y,max_y]).any() == np.NAN:
        #     # experimetal
        #     width  = self.eyeScreen.width
        #     height = self.eyeScreen.height
        #     if abs((max_x - min_x) - self.eyeScreen.width) > 0.1:
        #         width = (max_x - min_x)
        #     if abs((max_y - min_y) - self.eyeScreen.height) > 0.1:
        #         height = (max_y - min_y)

        #     self.eyeScreen.setWH(width,height)


        # ====================================
        
        p = self.eyeScreen.convertToScreen(point) - (100,0)

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