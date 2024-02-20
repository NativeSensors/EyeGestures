import numpy as np

class Heatmap():

    def __init__(self,width,height,buffor):
        bars = 10
        self.inc_step = 10
        self.step = bars

        bars_x = int(width/bars)
        bars_y = int(height/bars)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

        for point in buffor:
            x = point[0]
            y = point[1]

            self.axis_x[int(x/bars % width/bars)] += self.inc_step
            self.axis_y[int(y/bars % height/bars)] += self.inc_step

        self.min_x = self.__getParam((self.axis_x > self.inc_step*2),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*2),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*2),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*2),last=True)

    def __getParam(self,param,last : bool = False):
        ret = 0
        retArray = np.where(param)
        
        if len(retArray[0]) > 0:
            ret = retArray[0][- int(last)] * self.step

            if not ret == np.NAN:
                ret = int(ret)
        
        return ret
        
    def getBoundaries(self):
        x = self.min_x
        y = self.min_y
        w = self.max_x - self.min_x
        h = self.max_y - self.min_y 
        return (x,y,w,h)

    def getCenter(self):
        center_x = int((self.max_x - self.min_x)/2 + self.min_x)
        center_y = int((self.max_y - self.min_y)/2 + self.min_y)
        return (center_x,center_x)
    
    def getPeak(self):
        x = int(np.argmax(self.axis_x)*self.inc_step)
        y = int(np.argmax(self.axis_y)*self.inc_step)
        return (x,y)

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)
