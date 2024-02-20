import numpy as np

class Heatmap():

    def __init__(self,width,height,buffor):
        print(width,height)
        self.inc_step = 10
        self.step = 10
        bars = self.step

        self.width = width
        self.height = height

        bars_x = int(width/self.step)
        bars_y = int(height/self.step)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

        for point in buffor:
            x = point[0]
            y = point[1]

            print(x,y,int(x/bars),int(y/bars),self.axis_x.shape,self.axis_y.shape)
            self.axis_x[int(x/bars)] += self.inc_step
            self.axis_y[int(y/bars)] += self.inc_step

        self.min_x = self.__getParam((self.axis_x > self.inc_step*4),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*4),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*4),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*4),last=True)
        print(self.min_x,self.max_x,self.min_y,self.max_y)

    def __getParam(self,param,last : bool = False):
        ret = 0
        retArray = np.where(param)
        
        if len(retArray[0]) > 0:
            ret = retArray[0][- int(last)] * self.step
            print(ret,retArray[0][- int(last)])

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
        return (center_x,center_y)
    
    def getPeak(self):
        x = int(np.argmax(self.axis_x)*self.inc_step)
        y = int(np.argmax(self.axis_y)*self.inc_step)
        return (x,y)

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)
