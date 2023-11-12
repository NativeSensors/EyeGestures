import cv2
import math
import numpy as np
import eyeGestures.pupil as pupil

class PolarEye:

    REFERENCE_KEYPOINT = 0

    def __init__(self,pupil,landmarks, center):
        self.pupil     = pupil[0] 
        self.landmarks = landmarks
        self.center    = center

        self.__process(pupil,landmarks)
        pass

    def __convert2polar(self,point):
        (x,y) = point
        (cx,cy) = self.center
        (x,y) = (x - cx,y - cy)

        angle = math.atan2(y,x)*180/np.pi
        if angle < 0:
            angle += 360
        r = math.dist([0,0],[x,y])

        return (r,angle)

    def __convert2cartesian(self,r,angle):
        x = r*math.sin(angle)
        y = r*math.cos(angle)
        
        return (x,y)


    def __process(self,pupil,landmarks):
        desired_angle = 180
        _,ref_angle = self.__convert2polar(landmarks[self.REFERENCE_KEYPOINT])
        self.correction_angle = ref_angle - desired_angle 


    def getPupil(self):
        return np.array(
            self.__convert2polar(self.pupil)) 

    def getCorrectedPupil(self):
        (r, angle) = self.__convert2polar(self.pupil) 
        return np.array(
            self.__convert2cartesian(r, angle - self.correction_angle))

    def getLandmarks(self):
        landmarks_polar = []
        for point in self.landmarks:
            landmarks_polar.append(self.__convert2polar(point))
        return np.array(landmarks_polar)

    def getCorrectedLandmarks(self):
        landmarks_polar = []
        for point in self.landmarks:
            (r, angle) = self.__convert2polar(point) 
            landmarks_polar.append(
                self.__convert2cartesian(r, angle - self.correction_angle))
        return np.array(landmarks_polar)

        


class Eye:    
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    def __init__(self,image : np.ndarray, landmarks : list, side : int):
        self.image = image
        self.landmarks = landmarks

        # check if eye is left or right
        if side == 1:
            self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        elif side == 0:
            self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self._process(self.image,self.region)

        #getting polar coordinates
        self.polar = PolarEye(self.pupil.getCoords(),self.region,(self.center_x,self.center_y))

    def getPupil(self):
        return self.pupil.getCoords()

    def getLandmarks(self):
        return self.region 

    def getPolar(self):
        return self.polar

    def _process(self,image,region):
        points = np.array([[100, 50], [200, 150], [300, 50]], dtype=np.int32)

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

        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

        cut_image = masked_image[min_y:max_y,min_x:max_x] 
  
        self.pupil = pupil.Pupil(cut_image,min_x,min_y)


            