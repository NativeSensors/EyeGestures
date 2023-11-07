import cv2
import dlib
import time
import queue
import pickle
import random
import threading
import numpy as np
from typing import Callable, Tuple
from utils.eyetracker import EyeSink, EyeTracker, CalibrationCollector, CalibrationDisplay
from utils.utils import detectFace, getEyes, getCoordinates, var, VideoCapture

if __name__ == "__main__":    
    frames = []
    with open('recording/calibrationData1.pkl', 'rb') as file:
        frames = pickle.load(file)
    
    facePredictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    faceDetector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # use half of the data for fitting
    pFrame = None
    flow = None
    for _, frame in frames:
        
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        (x, y, w, h) = faceDetector.detectMultiScale(gray, 1.1, 9)[0]
        landmarks  = facePredictor(gray, dlib.rectangle(x, y, x+w, y+h))
        rect = landmarks.rect
        lt_corner = (rect.left(),rect.top())
        rb_corner = (rect.right(),rect.bottom())
        cv2.rectangle(frame,lt_corner,rb_corner,(0,0,255),1)

        faceFrame = cv2.resize(gray[rect.top():rect.bottom(),rect.left():rect.right()],(420,420))
        
        # check if previous frame is filled if it is not then fill it
        if pFrame is None:
            pFrame = faceFrame

        cv2.imshow("frame",frame) 

        # Parameters for Farneback optical flow
        # Note: These are example parameters and may need to be adjusted for your specific use case
        flow_params = dict(pyr_scale=0.9,    # Scaling between pyramid levels
                        levels=3,          # Number of pyramid levels
                        winsize=15,         # Averaging window size
                        iterations=3,      # Number of iterations at each pyramid level
                        poly_n=5,          # Size of the pixel neighborhood used to find polynomial expansion
                        poly_sigma=1.2,    # Standard deviation of the Gaussian used to smooth derivatives
                        flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN)

        # Calculate optical flow
        print(f"pFrame: {pFrame.shape} , faceFrame: {faceFrame.shape}")
        flow = cv2.calcOpticalFlowFarneback(pFrame, faceFrame, flow, **flow_params)
        
        # The flow is a 2-channel numpy array with the first channel corresponding to the horizontal and the second to the vertical flow.
        # For visualization, you might want to map the flow vectors into color space, e.g., HSV, and then convert to BGR for display with OpenCV
        # h, w = pFrame.shape[:2]
        # flow_hsv = np.zeros((h, w, 3), dtype=np.uint8)
        # magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # flow_hsv[..., 0] = angle * 180 / np.pi / 2
        # flow_hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        # flow_hsv[..., 1] = 255

        # flow_bgr = cv2.cvtColor(flow_hsv, cv2.COLOR_HSV2BGR)


        flow_img = np.zeros((h, w, 3), dtype=np.uint8)
        # Decide on the density of the vectors (you may want to adjust this)
        step = 3
        # Draw the flow vectors
        for y in range(0, h, step):
            for x in range(0, w, step):
                # Get the flow vector at this position
                fx, fy = flow[y, x]

                # Draw a line from this position to the end position
                end_x = int(x + fx)
                end_y = int(y + fy)
                cv2.line(flow_img, (x, y), (end_x, end_y), (255, 0, 0), 2)
                
                # Draw a circle at the end to indicate the direction
                cv2.circle(flow_img, (end_x, end_y), 1, (0, 255, 0), 2)


        # Display the result
        cv2.imshow('Optical Flow', flow_img)

        if cv2.waitKey(10) == ord('q'):
            run = False
            break                        
        #show point on sandbox
        pFrame = faceFrame

    cv2.destroyAllWindows()