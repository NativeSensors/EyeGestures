import cv2
import math
import numpy as np
import eyeGestures.pupil as pupil

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

    def getPupil(self):
        return self.pupil.getCoords()

    def getLandmarks(self):
        return self.region 

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

        cut_image = masked_image[min_y:max_y,min_x:max_x] 
  
        self.pupil = pupil.Pupil(cut_image,min_x,min_y)


            