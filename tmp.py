import cv2
import time
import pickle 
import numpy as np
from utils.eyeframes import eyeFrame, eyeFrameStorage
import cv2
import dlib

predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

def getEyes(gray):
    # Detect faces
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    eye_images = []
    for (x, y, w, h) in eyes:
        eye_images.append(gray[y:y+h,x:x+w])
        # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return eye_images

def getFaces(gray):
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    facial_landmarks = []
    faces_images = []
    for (x, y, w, h) in faces:
        drect = dlib.rectangle(x, y, w, h)
        tmp = predictor(gray,drect)
        facial_landmarks.append(shape_to_np(tmp))

        faces_images.append(gray[y:y+h,x:x+w])
        # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return faces_images,facial_landmarks


if __name__ == "__main__":
    framesStorage = eyeFrameStorage()

    #print("Before URL")
    cap = cv2.VideoCapture('rtsp://192.168.18.14:8080/h264.sdp')
    #print("After URL")

    # Load the cascade

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    # Read the input image

    # Get the current time
    while True:

        #print('About to start the Read command')
        ret, frame = cap.read()
        #print('Running..')
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces,facial_landmarks = getFaces(gray)
        
        if len(faces) > 0:
            
            face = faces[0]
            facial_landmarks = facial_landmarks[0]

            
            left_face = face[:int(face.shape[0]/2),:int(face.shape[0]/2)]
            right_face = face[:int(face.shape[0]/2),int(face.shape[0]/2):]
            leftEye = eyeFrame(getEyes(left_face))
            rightEye = eyeFrame(getEyes(right_face))

            print(leftEye)
            # left_eyes_landmarks = facial_landmarks[LEFT_EYE_KEYPOINTS]

            # x_left_offset = int(face.shape[0]/2) + leftEye
            # y_left_offset = int(face.shape[0]/2) +
            
            # left_eyes_landmarks[:,0] += x_left_offset 
            # left_eyes_landmarks[:,1] += y_left_offset

            # right_eyes_landmarks = facial_landmarks[RIGHT_EYE_KEYPOINTS] 

            if len(leftEye.get()) > 0:
                cv2.imshow(f'left_eye', leftEye.get()[0])
            
            if len(rightEye.get()) > 0:    
                cv2.imshow(f'right_eye', rightEye.get()[0])

            if cv2.waitKey(1) == ord('q'):
                break

            framesStorage.append([leftEye,rightEye])

    with open(f'recording/data{time.time()}.pkl', 'wb') as file:
        pickle.dump(framesStorage, file)

    cap.release()
    cv2.destroyAllWindows()
