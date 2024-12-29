import numpy as np
import sklearn.linear_model as scireg
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import asyncio
import threading

def euclidean_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

class Calibrator:

    PRECISION_LIMIT = 50
    PRECISION_STEP = 10
    ACCEPTANCE_RADIUS = 500

    def __init__(self,CALIBRATION_RADIUS=1000):
        self.X = []
        self.Y_y = []
        self.Y_x = []
        self.__tmp_X = []
        self.__tmp_Y_y = []
        self.__tmp_Y_x = []
        self.reg = None
        self.reg_x = scireg.Ridge(alpha=0.5)
        self.reg_y = scireg.Ridge(alpha=0.5)
        self.current_algorithm = "Ridge"
        self.fitted = False
        self.cv_not_set = True

        self.matrix = CalibrationMatrix()
        
        self.precision_limit = self.PRECISION_LIMIT
        self.precision_step = self.PRECISION_STEP
        self.acceptance_radius = int(CALIBRATION_RADIUS/2)
        self.calibration_radius = int(CALIBRATION_RADIUS)

        self.lock = threading.Lock()
        self.calcualtion_coroutine = threading.Thread(target=self.__async_post_fit)
        self.fit_coroutines = [] 

    def __launch_fit(self):
        coroutine = threading.Thread(target=self.__async_fit)
        self.fit_coroutines.append(coroutine)
        coroutine.start()
        self.__join_finished()

    def __join_finished(self):
        for coroutine in self.fit_coroutines:
            if not coroutine.is_alive():
                coroutine.join()


    def add(self,x,y):
        with self.lock:
            self.__tmp_X.append(x.flatten())
            self.__tmp_Y_y.append(y[1])
            self.__tmp_Y_x.append(y[0])
            self.__launch_fit()

    # This coroutine helps to asynchronously recalculate results
    def __async_fit(self):
        try:
            with self.lock:
                __fit_tmp_X   = np.array(self.__tmp_X + self.X, dtype=object)
                __fit_tmp_Y_y = np.array(self.__tmp_Y_y + self.Y_y)
                __fit_tmp_Y_x = np.array(self.__tmp_Y_x + self.Y_x)
                self.reg_x.fit(__fit_tmp_X,__fit_tmp_Y_x)
                self.reg_y.fit(__fit_tmp_X,__fit_tmp_Y_y)
                self.fitted = True
        except Exception as e:
            print(f"Exception as {e}")

    # This coroutine helps to asynchronously recalculate results
    def __async_post_fit(self):
        try:
            tmp_fixations_x = scireg.LassoCV(cv=50,max_iter=10000)
            tmp_fixations_y = scireg.LassoCV(cv=50,max_iter=10000)

            __tmp_X   = np.array(self.X)
            __tmp_Y_y = np.array(self.Y_y)
            __tmp_Y_x = np.array(self.Y_x)

            tmp_fixations_x.fit(__tmp_X,__tmp_Y_x)
            tmp_fixations_y.fit(__tmp_X,__tmp_Y_y)

            with self.lock:
                self.fixations_x = tmp_fixations_x
                self.fixations_y = tmp_fixations_y
                self.fitted = True
                self.current_algorithm = "LassoCV"
        except Exception as e:
            print(f"Exception as {e}")
            self.cv_not_set = True
        pass

    def post_fit(self):
        if self.cv_not_set:
            # self.calcualtion_coroutine.start()
            self.cv_not_set = False

    def whichAlgorithm(self):
        with self.lock:
            return self.current_algorithm

    def predict(self,x):
        with self.lock:
            if self.fitted:
                x = x.flatten()
                x = x.reshape(1, -1)
                y_x = self.reg_x.predict(x)[0]
                y_y = self.reg_y.predict(x)[0]
                return np.array([y_x,y_y])
            else:
                return np.array([0.0,0.0])

    def movePoint(self):
        with self.lock:
            self.X =   self.X + self.__tmp_X
            self.Y_y = self.Y_y + self.__tmp_Y_y
            self.Y_x = self.Y_x + self.__tmp_Y_x
            self.matrix.movePoint()
            self.__tmp_X = []
            self.__tmp_Y_y = []
            self.__tmp_Y_x = []

    def isReadyToMove(self):
        return len(self.__tmp_X) > 30 # magic number - collect 30 points

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