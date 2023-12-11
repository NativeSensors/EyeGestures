
import numpy as np
from eyeGestures.nose import NoseDirection
from eyeGestures.face import FaceFinder
from eyeGestures.calibration   import GazePredictor, CalibrationData
from eyeGestures.processing    import EyeProcessor
from eyeGestures.screenTracker import ScreenManager

class Gevent:

    def __init__(self,point,point_screen,blink,fixation,l_eye,r_eye,screen_man):

        self.point = point
        self.blink = blink
        self.fixation = fixation
        self.point_screen = point_screen
        
        ## ALL DEBUG DATA
        self.l_eye = l_eye
        self.r_eye = r_eye
        self.screen_man = screen_man

class Fixation:

    def __init__(self,x,y,radius = 100):
        self.radius = radius
        self.fixation = 0.0
        self.x = x 
        self.y = y
        pass

    def process(self,x,y):
        
        if (x - self.x)**2 + (y - self.y)**2 < self.radius**2:
            self.fixation = min(self.fixation + 0.02, 1.0)
        else:
            self.x = x
            self.y = y
            self.fixation = 0

        return self.fixation
class GazeTracker:

    N_FEATURES = 16

    def __init__(self,screen_width,screen_heigth,
                 eye_screen_w,eye_screen_h,
                 monitor_offset_x = 0,
                 monitor_offset_y = 0):

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h

        self.eyeProcessorLeft  = EyeProcessor(eye_screen_w,eye_screen_h)
        self.eyeProcessorRight = EyeProcessor(eye_screen_w,eye_screen_h)

        self.screen_man = ScreenManager(screen_width,
                                        screen_heigth,
                                        self.eye_screen_w,
                                        self.eye_screen_h,
                                        monitor_offset_x,
                                        monitor_offset_y)

        self.noseDirection = NoseDirection()
        self.predictor = GazePredictor()
        self.finder = FaceFinder()

        self.gazeFixation = Fixation(0,0,100)

        self.calibrationData = CalibrationData()

        self.buffor = []
        self.bufforLength = 10

        # those are used for analysis
        self.__debugBuffer = []
        self.__debugCalibBuffer = []
        self.__headDir = [0.5,0.5]

        self.point_screen = [0.0,0.0]

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

            eyes = np.concatenate((llandmards,lpupil,rlandmards,rpupil))
            if np.isnan(eyes).any():
                eyes = np.full((self.N_FEATURES,2),np.NAN)

        return np.array(eyes) 
    
    def __gaze_intersection(self,l_eye,r_eye):
        l_pupil = l_eye.getPupil()
        l_gaze  = l_eye.getGaze()
        
        r_pupil = r_eye.getPupil()        
        r_gaze  = r_eye.getGaze()

        l_end = l_gaze + l_pupil
        r_end = r_gaze + r_pupil

        l_m = (l_end[1] - l_pupil[1])/(l_end[0] - l_pupil[0])
        r_m = (r_end[1] - r_pupil[1])/(r_end[0] - r_pupil[0])

        l_b = l_end[1] - l_m * l_end[0]
        r_b = r_end[1] - r_m * r_end[0]

        i_x = (r_b - l_b)/(l_m - r_m)
        i_y = r_m * i_x + r_b
        return (i_x,i_y)

    def __gaussian_weight(self, distance, sigma=1.0):
        # Gaussian function to assign a weight based on distance
        # e^(dist^2/(2*sigma^2))
        return np.exp(-distance**2 / (2 * sigma**2))

    # that can be useful to stabilise data 
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

        face = self.getFeatures(image)

        if not face is None:
        
            l_eye = face.getLeftEye()
            r_eye = face.getRightEye()

            l_pupil = l_eye.getPupil()
            r_pupil = r_eye.getPupil()
            
            blink = l_eye.getBlink() or r_eye.getBlink()
            
            intersection_x,_ = self.__gaze_intersection(l_eye,r_eye)

            # TODO: check what happens here before with l_pupil
            self.eyeProcessorLeft.append( l_pupil, l_eye.getLandmarks())
            self.eyeProcessorRight.append(r_pupil, r_eye.getLandmarks())

            # This scales pupil move to the screen we observe
            point = self.eyeProcessorLeft.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            l_point = np.array((int(intersection_x),point[1]))

            point = self.eyeProcessorRight.getAvgPupil(self.eye_screen_w,self.eye_screen_h)
            r_point = np.array((int(intersection_x),point[1]))

            compound_point = np.array(((l_point + r_point)/2),dtype=np.uint32)

            if blink == True:
                return None
            
            self.point_screen = self.screen_man.process(compound_point)

            fixation = self.gazeFixation.process(self.point_screen[0],self.point_screen[1])        
            blink = blink and (fixation > 0.8)

            return Gevent(compound_point,
                        self.point_screen,
                        blink,
                        fixation,
                        l_eye,
                        r_eye,
                        self.screen_man)

        return None
    
    def calibrate(self,calibrationPoint,image):

        features = self.__getFeatures(image)

        if np.isnan(features).any():
            pass
        else:
            self.__debugBuffer.append(features)
            self.__debugCalibBuffer.append(calibrationPoint)

            self.calibrationData.add(calibrationPoint,features)

    def getCalibration(self):
        return self.calibrationData.get()

    def getFeatures(self,image):
        face = self.finder.find(image)
        return face
        
    def getHeadDirection(self):
        return self.__headDir        