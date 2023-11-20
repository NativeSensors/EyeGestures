import cv2
import math
import numpy as np
import mediapipe as mp
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
    LEFT_EYE_KEYPOINTS  = np.array(list(mp.solutions.face_mesh.FACEMESH_LEFT_EYE))[:,0]
    RIGHT_EYE_KEYPOINTS = np.array(list(mp.solutions.face_mesh.FACEMESH_RIGHT_EYE))[:,0]
    LEFT_EYE_PUPIL_KEYPOINT  = [468]
    RIGHT_EYE_PUPIL_KEYPOINT = [473]
        
    # LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    # RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    scale = (150,100)

    def __init__(self,image : np.ndarray, landmarks : list, side : int):
        self.gaze_buff = Buffor(20)
        self.eyeBuffer = Buffor(2)
        
        self.image = image
        self.landmarks = landmarks

        # check if eye is left or right
        if side == 1:
            self.side = "right"
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
            self.pupil_index = self.RIGHT_EYE_PUPIL_KEYPOINT
        elif side == 0:
            self.side = "left"
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
            self.pupil_index = self.LEFT_EYE_PUPIL_KEYPOINT
        
        self.pupil = landmarks[self.pupil_index][0]
        self._process(self.image,self.region)

    def update(self,image : np.ndarray, landmarks : list):
        self.image = image
        self.landmarks = landmarks
        # check if eye is left or right
        if self.side == "right":
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        
        elif self.side == "left":
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self.pupil = landmarks[self.pupil_index][0]
        self._process(self.image,self.region)


    def getPupil(self):
        # return self.pupil.getCoords()
        return self.pupil

    def getImage(self):
        return self.cut_image

    def getGaze(self):
        pupilCoords = self.pupil.getCoords()
        
        sumY = 0
        sumX = 0

        print(f"self.width: {self.width},self.height: {self.height}")
        # if(self.width > 2*self.height):
        #     __region = self.region[0:-1]
        # else:
        __region = self.region

        for point in __region:
            (x,y) = (point[0] - self.pupil[0],point[1] - self.pupil[1])

            sumY += y
            sumX += x

        ret_point = (-sumX,-sumY)
        self.gaze_buff.add(ret_point)
        
        return self.gaze_buff.getAvg()
        
    def getOpenness(self):
        return self.height

    def getLandmarks(self):
        return self.region 

    def _process(self,image,region):

        h, w, _ = image.shape

        mask = np.full((h, w), 255, dtype=np.uint8) 
        background = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [region], 0)

        masked_image = cv2.bitwise_not(background, image.copy(), mask=mask)
        
        margin = 5
        min_x = np.min(region[:,0]) - margin
        max_x = np.max(region[:,0]) + margin
        min_y = np.min(region[:,1]) - margin
        max_y = np.max(region[:,1]) + margin

        self.width  = np.max(region[:,0]) - np.min(region[:,0])
        self.height = np.max(region[:,1]) - np.min(region[:,1])
        
        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

        # self.intersection = getIntersections(region,self.center_y)
        self.cut_image = masked_image[min_y:max_y,min_x:max_x] 
        self.cut_image = cv2.resize(self.cut_image,self.scale)
        
        # save cut_image to buffor and get avg from previous buffors 
        # self.eyeBuffer.add(self.cut_image)
        # self.cut_image = np.array(self.eyeBuffer.getAvg(), dtype=np.uint8) 
            
        # LEGACY
        # org_scale = (max_x - min_x,max_y - min_y)
        # self.pupil = pupil.Pupil(self.cut_image, min_x, min_y, self.scale, org_scale)
        

            