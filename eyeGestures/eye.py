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


class EyeTiles:

    def __init__(self, start_x, start_y, width, height, nx_tiles = 3, ny_tiles = 1):
        self.start_x = start_x
        self.start_y = start_y
        self.width  = width
        self.height = height

        self.nx_tiles = nx_tiles
        self.ny_tiles = ny_tiles

        self.x_step = self.width/nx_tiles
        self.y_step = self.height/ny_tiles

        self.x_tiles = []
        for n in self.nx_tiles:
            self.x_tiles.append(EyeTile(self.start_x+self.x_step*n,self.start_x+self.x_step*(n+1)))

        self.y_tiles = []
        for n in self.ny_tiles:
            self.y_tiles.append(EyeTile(self.start_y+self.y_step*n,self.start_y+self.y_step*(n+1)))

        pass

    def getActiveTile(self,x,y):
        x_n,y_n = 0,0
        for n,tile in enumerate(self.x_tiles):
            if tile.isTileActive():
                x_n = n

        for n,tile in enumerate(self.x_tiles):
            if tile.isTileActive():
                y_n = n

        return (x_n,y_n)

class EyeTile:

    def __init__(self,lower_limit,high_limit):
        self.lower_limit = lower_limit
        self.high_limit  = high_limit
        pass

    def isTileActive(self,position):
        if self.lower_limit < position and self.high_limit < position:
            return True
        return False

class Eye:    
    LEFT_EYE_KEYPOINTS  = np.array(list(mp.solutions.face_mesh.FACEMESH_LEFT_EYE))[:,0]
    RIGHT_EYE_KEYPOINTS = np.array(list(mp.solutions.face_mesh.FACEMESH_RIGHT_EYE))[:,0]
    LEFT_EYE_IRIS_KEYPOINT  = []
    RIGHT_EYE_IRIS_KEYPOINT = []
    LEFT_EYE_PUPIL_KEYPOINT  = [473]
    RIGHT_EYE_PUPIL_KEYPOINT = [468]
        
    # LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    # RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    scale = (150,100)

    def __init__(self,image : np.ndarray, landmarks : list, side : int, offset : np.ndarray):
        self.gaze_buff = Buffor(20)
        self.eyeBuffer = Buffor(2)
        
        self.image = image
        self.offset = offset
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

    def update(self,image : np.ndarray, landmarks : list, offset : np.ndarray):
        self.image = image
        self.offset = offset
        self.landmarks = landmarks

        # check if eye is left or right
        if self.side == "right":
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        
        elif self.side == "left":
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self.pupil = landmarks[self.pupil_index][0]
        self._process(self.image,self.region)

    def getCenter(self):
        return (self.center_x,self.center_y)

    def getPos(self):
        return (self.x,self.y)

    def getPupil(self):
        # return self.pupil.getCoords()
        return self.pupil
    
    def getBlink(self):
        # return self.pupil.getCoords()
        return (self.height) <= 3 # 2x margin 

    def getImage(self):
        # TODO: draw additional parameters
        return self.cut_image

    def getGaze(self,y_correction=0,x_correction=0):
        # pupilCoords = self.pupil.getCoords()
        center = np.array((self.center_x,self.center_y)) - self.offset
        
        region_corrected = self.region - self.offset
        pupil_corrected = self.pupil - self.offset

        vectors = region_corrected  - center
        pupil = pupil_corrected - center
        
        vectors = vectors - pupil
        gaze_vector = np.zeros((2))
        
        gaze_vector[1] = np.sum(vectors, axis=0)[1] * 10 - y_correction
        gaze_vector[0] = -np.sum(vectors, axis=0)[0] * 10 - x_correction
        
        print("gaze_vector: ",gaze_vector)
        self.gaze_buff.add(gaze_vector)   
        return self.gaze_buff.getAvg()
        
    def getOpenness(self):
        return self.height/2 

    def getLandmarks(self):
        return self.region 

    def _process(self,image,region):
        h, w, _ = image.shape

        mask = np.full((h, w), 0, dtype=np.uint8) 
        background = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [region], 0)

        masked_image = cv2.bitwise_not(background, cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY), mask=mask)
        
        margin = 2
        min_x = np.min(region[:,0]) - margin
        max_x = np.max(region[:,0]) + margin
        min_y = np.min(region[:,1]) - margin
        max_y = np.max(region[:,1]) + margin
        
        self.x = min_x
        self.y = min_y
        
        self.width  = np.max(region[:,0]) - np.min(region[:,0])
        self.height = np.max(region[:,1]) - np.min(region[:,1])
        
        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

        # HACKETY_HACK: 
        self.pupil[1] = np.min(region[:,1])
    
        # self.intersection = getIntersections(region,self.center_y)
        self.cut_image = masked_image[min_y:max_y,min_x:max_x]
        # print(f"here: {self.cut_image.shape,min_y,max_y,min_x,max_x}")
        self.cut_image = cv2.cvtColor(self.cut_image, cv2.COLOR_GRAY2BGR)
        
        for point in self.region:
            point = point - (min_x,min_y)
            cv2.circle(self.cut_image,point.astype(int),1,(255,0,0,150),1)

        pupil = self.pupil - (min_x,min_y)

        # print(f"pupil: {pupil}")
        cv2.circle(self.cut_image,pupil.astype(int),1,(0,255,0,150),1)

        self.cut_image = cv2.resize(self.cut_image,self.scale)
        
        # save cut_image to buffor and get avg from previous buffors 
        # self.eyeBuffer.add(self.cut_image)
        # self.cut_image = np.array(self.eyeBuffer.getAvg(), dtype=np.uint8) 
            
        # LEGACY
        # org_scale = (max_x - min_x,max_y - min_y)
        # self.pupil = pupil.Pupil(self.cut_image, min_x, min_y, self.scale, org_scale)
        

            