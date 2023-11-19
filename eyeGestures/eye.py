import cv2
import math
import numpy as np
import eyeGestures.pupil as pupil
from scipy.optimize import fsolve
from eyeGestures.utils import Buffor

# Function to fit a quadratic curve and find intersections
def fit_curve(p1, p2):
    # Fit a quadratic curve (ax^2 + bx + c) through the points
    coefficients = np.polyfit([p1[0], p2[0]], [p1[1], p2[1]], 2)
    curve = np.poly1d(coefficients)

    return curve

# Function to find intersections with y = 0
def find_intersections(curve, points):
    def intersection(x):
        return curve(x)

    intersection_points = fsolve(intersection, 0)
    return (intersection_points,0)

def getCurves(points, reference_point):
    segments = []
    intersection_points = []
    for i in range(len(points)):
        p1, p2 = points[i], points[(i + 1 ) % len(points)]
        if (p1[1] - reference_point) * (p2[1] - reference_point) < 0:
            curve = fit_curve(p1, p2)
            
            segment_x_range = np.linspace(p1[0], p2[0], 100)
            segments.append((curve,segment_x_range))
            x = find_intersections(curve,np.array([p1, p2]))
            intersection_points.append(x)

    return segments,intersection_points

def getIntersections(points, reference_point):
    _, intersetions = getCurves(points, reference_point)
    return np.array(intersetions)

    
class Eye:    
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    scale = (150,100)

    def __init__(self,image : np.ndarray, landmarks : list, side : int):
        self.gaze_buff = Buffor(10)
        self.eyeBuffer = Buffor(2)
        
        self.image = image
        self.landmarks = landmarks

        # check if eye is left or right
        if side == 1:
            self.side = "right"
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        elif side == 0:
            self.side = "left"
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self._process(self.image,self.region)

    def update(self,image : np.ndarray, landmarks : list):
        self.image = image
        self.landmarks = landmarks
        # check if eye is left or right
        if self.side == "right":
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        elif self.side == "left":
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self._process(self.image,self.region)


    def getPupil(self):
        return self.pupil.getCoords()

    def getImage(self):
        return self.cut_image

    def getGaze(self):
        pupilCoords = self.pupil.getCoords()
        
        sumY = 0
        sumX = 0

        __region = self.region

        for point in __region:
            (x,y) = (point[0] - pupilCoords[0],point[1] - pupilCoords[1])

            sumY += y
            sumX += x

        ret_point = (-sumX*self.height/self.width,sumY)
        self.gaze_buff.add(ret_point)
        
        return self.gaze_buff.getAvg()
        
    # def getIntersection(self):
    #     return self.pupil.getCoords()

    def getLandmarks(self):
        return self.region 

    def _process(self,image,region):

        h, w = image.shape
        mask = np.full((h, w), 255, dtype=np.uint8) 
        background = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [region], 0)

        masked_image = cv2.bitwise_not(background, image.copy(), mask=mask)
        
        margin = 5
        min_x = np.min(region[:,0]) - margin
        max_x = np.max(region[:,0]) + margin
        min_y = np.min(region[:,1]) - margin
        max_y = np.max(region[:,1]) + margin

        self.width  = max_x - min_x
        self.height = max_y - min_y
        print(f"eye openness: {self.height}")

        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

        # self.intersection = getIntersections(region,self.center_y)
        self.cut_image = masked_image[min_y:max_y,min_x:max_x] 
        self.cut_image = cv2.resize(self.cut_image,self.scale)
        
        # save cut_image to buffor and get avg from previous buffors 
        self.eyeBuffer.add(self.cut_image)
        self.cut_image = np.array(self.eyeBuffer.getAvg(), dtype=np.uint8) 
            
        org_scale = (self.width,self.height)
        self.pupil = pupil.Pupil(self.cut_image, min_x, min_y, self.scale, org_scale)
        

            