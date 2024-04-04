import numpy as np

class Heatmap():
    """Helper representing Heatmap of tracked points"""

    def __init__(self,width,height,buffor):
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

            self.axis_x[min(abs(int(x/bars)),bars_x - 1)] += self.inc_step
            self.axis_y[min(abs(int(y/bars)),bars_x - 1)] += self.inc_step

        self.min_x = self.__getParam((self.axis_x > self.inc_step*4),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*4),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*4),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*4),last=True)

    def __getParam(self,param,last : bool = False):
        ret = 0
        retArray = np.where(param)

        if len(retArray[0]) > 0:
            ret = retArray[0][- int(last)] * self.step

            if not ret == np.NAN:
                ret = int(ret)

        return ret

    def getBoundaries(self):
        """Function returning boundaries of heatmap"""
        x = self.min_x
        y = self.min_y
        w = self.max_x - self.min_x
        h = self.max_y - self.min_y
        return (x,y,w,h)

    def getCenter(self):
        """Function returning center of heatmap"""
        center_x = int((self.max_x - self.min_x)/2 + self.min_x)
        center_y = int((self.max_y - self.min_y)/2 + self.min_y)
        return (center_x,center_y)

    def getPeak(self):
        """Function returning peak of heatmap"""
        x = int(np.argmax(self.axis_x)*self.inc_step)
        y = int(np.argmax(self.axis_y)*self.inc_step)
        return (x,y)

    def getHist(self):
        """Function returning histogram of the heatmap. This heatmap is simply 2d histogram, so this function returns values for each axis."""
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)
