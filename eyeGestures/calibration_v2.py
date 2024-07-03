import numpy as np
import sklearn.linear_model as scireg

def euclidean_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

class Calibrator:

    def __init__(self):
        self.X = []
        self.Y_y = []
        self.Y_x = []
        self.reg = None
        self.reg_x = scireg.Ridge(alpha=1.0)
        self.reg_y = scireg.Ridge(alpha=1.0)
        self.fitted = False

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

    def unfit(self):
        self.fitted = False

class CalibrationMatrix:

    def __init__(self):

        self.iterator = 0
        self.points = np.array([[1,0.5],[0.75,0.5],[0.5,0.5],[0.25,0.5],[0.0,0.5],
                                [1.0,1.0],[0.75,1.0],[0.5,1.0],[0.25,1.0],[0.0,1.0],
                                [1.0,0.0],[0.75,0.0],[0.5,0.0],[0.25,0.0],[0.0,0.0],
                                [0.0,0.75],[0.75,0.75],[0.5,0.75],[0.25,0.75],[0.0,0.75],
                                [1.0,0.25],[0.75,0.25],[0.5,0.25],[0.25,0.25],[0.0,0.25]])
        pass

    def update_calibration_matrix(self,points):
        self.points = points
        self.iterator = 0

    def getNextPoint(self,width=1.0,height=1.0):
        it = self.iterator
        self.iterator += 1
        self.iterator %= len(self.points)

        return np.array([self.points[it,0] * width, self.points[it,1] * height])