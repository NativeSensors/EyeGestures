import numpy as np
import sklearn.linear_model as scireg

def euclidean_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

class Calibrator:

    PRECISION_LIMIT = 50
    PRECISION_STEP = 10
    ACCEPTANCE_RADIUS = 500
    CALIBRATION_RADIUS = 1000

    def __init__(self):
        self.X = []
        self.Y_y = []
        self.Y_x = []
        self.reg = None
        self.reg_x = scireg.Ridge(alpha=1.0)
        self.reg_y = scireg.Ridge(alpha=1.0)
        self.fitted = False

        self.matrix = CalibrationMatrix()
        
        self.precision_limit = self.PRECISION_LIMIT
        self.precision_step = self.PRECISION_STEP
        self.acceptance_radius = self.ACCEPTANCE_RADIUS
        self.calibration_radius = self.CALIBRATION_RADIUS

    def add(self,x,y):
        self.X.append(x.flatten())
        self.Y_y.append(y[1])
        self.Y_x.append(y[0])

        __tmp_X =np.array(self.X)
        __tmp_Y_y =np.array(self.Y_y)
        __tmp_Y_x =np.array(self.Y_x)

        self.reg_x.fit(__tmp_X,__tmp_Y_x)
        self.reg_y.fit(__tmp_X,__tmp_Y_y)
        self.fitted = True

    def predict(self,x):
        if self.fitted:
            x = x.flatten()
            x = x.reshape(1, -1)
            y_x = self.reg_x.predict(x)[0]
            y_y = self.reg_y.predict(x)[0]
            return np.array([y_x,y_y])
        else:
            return np.array([0.0,0.0])

    def movePoint(self):
        self.matrix.movePoint()

    def getCurrentPoint(self,width,heigth):
        return self.matrix.getCurrentPoint(width,heigth)

    def updMatrix(self,points):
        return self.matrix.updMatrix(points)

    def unfit(self):
        self.acceptance_radius = self.ACCEPTANCE_RADIUS
        self.calibration_radius = self.CALIBRATION_RADIUS
        self.fitted = False

    def increase_precision(self):
        if self.acceptance_radius > self.precision_limit:
            self.acceptance_radius -= self.precision_step
        if self.calibration_radius > self.precision_limit and self.acceptance_radius < self.calibration_radius:
            self.calibration_radius -= self.precision_step

    def insideClbRadius(self,point,width,height):
        return euclidean_distance(point,self.getCurrentPoint(width,height)) < self.calibration_radius
    
    def insideAcptcRadius(self,point,width,height):
        return euclidean_distance(point,self.getCurrentPoint(width,height)) < self.acceptance_radius
    
class CalibrationMatrix:

    def __init__(self):

        self.iterator = 0
        self.points = np.array([[1,0.5],[0.75,0.5],[0.5,0.5],[0.25,0.5],[0.0,0.5],
                                [1.0,1.0],[0.75,1.0],[0.5,1.0],[0.25,1.0],[0.0,1.0],
                                [1.0,0.0],[0.75,0.0],[0.5,0.0],[0.25,0.0],[0.0,0.0],
                                [0.0,0.75],[0.75,0.75],[0.5,0.75],[0.25,0.75],[0.0,0.75],
                                [1.0,0.25],[0.75,0.25],[0.5,0.25],[0.25,0.25],[0.0,0.25]])
        pass

    def updMatrix(self,points):
        self.points = points
        self.iterator = 0

    def movePoint(self):
        self.iterator += 1
        self.iterator %= len(self.points)

    def getCurrentPoint(self,width=1.0,height=1.0):
        it = self.iterator
        return np.array([self.points[it,0] * width, self.points[it,1] * height])