import cv2
import math
import numpy as np
import eyeGestures.utils as utils


class Eye:    
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye


    def __init__(self,image : np.ndarray, landmarks : list, side : int):
        self.thersh = 35
        self.image = image
        self.landmarks = landmarks

        # check if eye is left or right
        if side == 1:
           self.region = np.array(landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)
        elif side == 0:
           self.region = np.array(landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)
        
        self._process(self.image,self.region) 
        
    def _sizeIris(self,iris):
        h, w = iris.shape
        w_pixels = cv2.countNonZero(iris)
        all_pixels = h*w

        # percentage of black pixels
        pb_pixels = 1.00 - w_pixels/all_pixels

        return pb_pixels
        
    def _getIris(self,image,threshold):

        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(image, 5, 5, 10)
        new_frame = cv2.erode(new_frame, kernel, iterations=1)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]
        
        return new_frame


    def _process(self,image,region):
        points = np.array([[100, 50], [200, 150], [300, 50]], dtype=np.int32)

        h, w = image.shape
        mask = np.full((h, w), 255, dtype=np.uint8) 
        background = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [region], 0)

        masked_image = cv2.bitwise_not(background, image.copy(), mask=mask)
        # masked_image = image
        
        margin = 5
        min_x = np.min(region[:,0]) - margin
        max_x = np.max(region[:,0]) + margin
        min_y = np.min(region[:,1]) - margin
        max_y = np.max(region[:,1]) + margin

        cut_image = masked_image[min_y:max_y,min_x:max_x] 
        cv2.imshow("masked_image", masked_image)

        #Find best Iris cadidate
        swipe = 5
        start = (self.thersh - swipe) * (self.thersh - swipe) >= 0
        end = 100
        images = []
        for threshold in range(start,end,swipe):
            iris = self._getIris(cut_image,threshold)
            print(f"thresh: {threshold}, iris: {self._sizeIris(iris)}")
            if self._sizeIris(iris) > 0.045:
                self.thersh = threshold
                break
            images.append(iris)
        
        grid = utils.make_image_grid(images,5,5)

        cv2.imshow("grid",grid)
        cv2.imshow("cut_image",cut_image)
    
        contours, _ = cv2.findContours(iris, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea)

        image_rgb = cv2.cvtColor(self.image,cv2.COLOR_GRAY2RGB)
        iris_rgb = cv2.cvtColor(iris,cv2.COLOR_GRAY2RGB)
        try:
            moments = cv2.moments(contours[-2])
            x = int(moments['m10'] / moments['m00']) 
            y = int(moments['m01'] / moments['m00'])
            
            cv2.circle(image_rgb,(x + min_x,y + min_y),1,(0,0,255),1)  
            cv2.circle(iris_rgb,(x,y),1,(0,0,255),1)  

        except (IndexError, ZeroDivisionError):
            pass

        for point in region:
            cv2.circle(image_rgb,(point[0],point[1]),1,(0,255,0),1)

        cv2.circle(image_rgb,(min_x,min_y),1,(255,0,0),1)
        cv2.circle(image_rgb,(max_x,max_y),1,(255,0,0),1)

        cv2.imshow("iris",iris_rgb)
        cv2.imshow("tracked eye", image_rgb)


            