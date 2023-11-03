import cv2
import dlib
import time
import pickle
import pyautogui
import numpy as np
from typing import Callable, Tuple
from utils.eyeframes import eyeFrame, faceTracker
from utils.eyetracker import EyeSink
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Make predictions for new data points
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

tracker = faceTracker()

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def detectFace(gray : np.ndarray, onFace : Callable[[np.ndarray, np.ndarray, np.ndarray, (int,int,int,int)], None]):
    # hog_face_detector = dlib.get_frontal_face_detector()

    for (x, y, w, h) in face_cascade.detectMultiScale(gray, 1.1, 9):
        
        landmarks  = shape_to_np(predictor(gray, dlib.rectangle(x, y, x+w, y+h)))
        faceSquare = gray[x:x+w,y:y+h]
        
        onFace(faceSquare ,landmarks, (x, y, w, h))

def getCoordinates(left_eye : np.ndarray, right_eye : np.ndarray, onCoordinates : Callable[[(int,int),(int,int)], None]): 

    (left_eye_region, left_eye_landmarks) = left_eye
    (right_eye_region, right_eye_landmarks) = right_eye
    sink = EyeSink()

    left  = sink.push(left_eye_region)
    right = sink.push(right_eye_region)

    left = np.array(left).reshape(1, 2)
    right = np.array(right).reshape(1, 2)

    left_eye_show = left_eye_region
    right_eye_show = right_eye_region

    onCoordinates(np.concatenate((left,left_eye_landmarks),axis=0),np.concatenate((right,right_eye_landmarks),axis=0))

def getEyes(image : np.ndarray,
            faceSquare : np.ndarray,
            landmarks : np.ndarray,
            coordinates : (int,int,int,int),
            onEyes : Callable[[np.ndarray,np.ndarray], None]):

    eFrame = eyeFrame()
    (x, y, w, h) = coordinates
    eFrame.setParams(image,faceSquare, landmarks, (x, y, w, h))
    tracker.update(eFrame)      
    
    left_eye_region     = eFrame.getLeftEye()
    left_eye_landmarks  = eFrame.getLeftEyeLandmarks()
    right_eye_region    = eFrame.getRightEye()
    right_eye_landmarks = eFrame.getRightEyeLandmarks()
    
    onEyes((left_eye_region,left_eye_landmarks),(right_eye_region,right_eye_landmarks))
