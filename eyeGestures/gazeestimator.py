
import cv2
import math
import numpy as np
from eyeGestures.nose import NoseDirection
from eyeGestures.face import FaceFinder
from eyeGestures.calibration import GazePredictor, CalibrationData
from eyeGestures.processing  import EyeProcessor

# TODO: this slowly changing into head tracker
class GazeTracker:

    N_FEATURES = 16

    def __init__(self):
        self.noseDirection = NoseDirection()
        self.predictor = GazePredictor()
        self.finder = FaceFinder()

        self.calibrationData = CalibrationData()

        self.buffor = []
        self.bufforLength = 10

        # those are used for analysis
        self.__debugBuffer = []
        self.__debugCalibBuffer = []
        self.__headDir = [0.5,0.5]

    def __getFeatures(self,image):
        
        eyes = np.full((self.N_FEATURES,2),np.NAN)
        face = self.finder.find(image)
        
        if not face is None:
            # self.__headDir = self.noseDirection.getPos(face.getNose())
            l_eye = face.getLeftEye()
            r_eye = face.getRightEye()
            
            llandmards = l_eye.getLandmarks()
            lpupil     = l_eye.getPupil()
            rlandmards = r_eye.getLandmarks()
            rpupil     = r_eye.getPupil()
            # faceBox    = face.getBoundingBox()

            eyes = np.concatenate((llandmards,lpupil,rlandmards,rpupil))
            if np.isnan(eyes).any():
                eyes = np.full((self.N_FEATURES,2),np.NAN)

        return np.array(eyes) 

    def __gaussian_weight(self, distance, sigma=1.0):
        # Gaussian function to assign a weight based on distance
        # e^(dist^2/(2*sigma^2))
        return np.exp(-distance**2 / (2 * sigma**2))


    def __weightedCentroid(self, points):
        # Calculate the pairwise distances between points
        distances = np.sqrt(((points[:, np.newaxis, :] - points[np.newaxis, :, :]) ** 2).sum(axis=2))

        # Apply the Gaussian function to the distances to get weights
        # Using a small sigma to ensure that farther points have significantly less weight
        weights = self.__gaussian_weight(distances, sigma=0.1)

        # Avoid division by zero by setting the diagonal to zero (distance from a point to itself)
        np.fill_diagonal(weights, 0)

        # Sum the weights for each point
        sum_weights = np.sum(weights, axis=1)

        # Calculate the weighted centroid
        weighted_centroid = np.sum(points.T * sum_weights, axis=1) / np.sum(sum_weights)
        if np.isnan(weighted_centroid).any():
            return points[0]
        return weighted_centroid


    def estimate(self,image):

        features = self.__getFeatures(image)
        if np.isnan(features).any():
            return np.full((1,2),np.NAN)

        point = self.predictor.predict(features)
        if len(self.buffor) > self.bufforLength:
            self.buffor.pop(0)
        self.buffor.append(point)

        return self.__weightedCentroid(np.array(self.buffor))

    def calibrate(self,calibrationPoint,image):

        features = self.__getFeatures(image)

        if np.isnan(features).any():
            pass
        else:
            self.__debugBuffer.append(features)
            self.__debugCalibBuffer.append(calibrationPoint)

            self.calibrationData.add(calibrationPoint,features)

    def fit(self):
        trainingMeasurementPoints,trainingCalibrationPoints = self.calibrationData.get()
        self.predictor.train(trainingCalibrationPoints,trainingMeasurementPoints)

    def getCalibration(self):
        return self.calibrationData.get()

    def getFeatures(self,image):
        face = self.finder.find(image)
        # if not face is None:
        #     self.__headDir = self.noseDirection.getPos(face.getNose())
        return face
        
    def getHeadDirection(self):
        return self.__headDir        