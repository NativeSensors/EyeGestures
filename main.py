import cv2
import dlib
import pickle
import numpy as np
from utils.eyeframes import eyeFrame, faceTracker
from utils.eyetracker import EyeSink

LEFT  = 0
RIGHT = 1

predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
tracker = faceTracker()
sandbox = np.zeros([512,512,3],dtype=np.uint8)
sandbox.fill(255)

def getFace(gray):
    # hog_face_detector = dlib.get_frontal_face_detector()

    for (x, y, w, h) in face_cascade.detectMultiScale(gray, 1.1, 9):
        
        landmarks  = shape_to_np(predictor(gray, dlib.rectangle(x, y, x+w, y+h)))
        faceSquare = gray[x:x+w,y:y+h]
        yield (faceSquare ,landmarks, (x, y, w, h))
  
    # for (x, y, w, h) in face_cascade.detectMultiScale(gray, 1.1, 4):
    # face = face_cascade.detectMultiScale(gray, 1.1, 4)[0] 
    # (x, y, w, h) = face
    # landmarks  = shape_to_np(predictor(gray, dlib.rectangle(x, y, w, h)))
    # faceSquare = gray[x:x+w,y:y+h]
    # return [(faceSquare ,landmarks)]
   
    # # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)

def getEye(image,eyeRect):
    print(f"eyeRect {eyeRect} ")
    (x,y,w,h) = eyeRect
    eyeImage = image[x:x+w,y:y+h]
    return eyeImage

def getCoordinates(image): 

    sink = EyeSink()

    (left_eye_region , right_eye_region) = getEyes(image)
    left = sink.push(left_eye_region)
    right = sink.push(right_eye_region)

    left_eye_show = left_eye_region
    right_eye_show = right_eye_region

    (lcX,lcY) = left
    (rcX,rcY) = right
    (h,w,c) = left_eye_show.shape
    cv2.circle(left_eye_show,(int(rcX*w),int(rcY*h)),2,(255,0,0),1)
    (h,w,c) = right_eye_show.shape
    cv2.circle(right_eye_show,(int(lcX*w),int(lcY*h)),2,(0,0,255),1)
    cv2.imshow("left_eye_region", left_eye_show)
    cv2.imshow("right_eye_region",right_eye_show)

    return (left,right)

    # print("returning zeros")
    # right = (0,0)
    # left = (0,0)
    # return (left,right)

def getEyes(image):
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for faceSquare, landmarks, (x, y, w, h) in getFace(gray):
        sandbox.fill(255)
        eFrame = eyeFrame()
        eFrame.setParams(image,faceSquare, landmarks, (x, y, w, h))
        tracker.update(eFrame)      
        
        left_eye_region  = eFrame.getLeftEye()
        right_eye_region = eFrame.getRightEye()
        return (left_eye_region,right_eye_region)

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords


if __name__ == "__main__":
    frames = []
    run = True

    with open('recording/data31-10-2023-17:53:21.pkl', 'rb') as file:
        frames = pickle.load(file)

    while run:
        for n, frame in enumerate(frames):
            w = frame.shape[1]
            h = frame.shape[0]

            scale_percent = 60 # percent of original size
            width = int(w * scale_percent / 100)
            height = int(h * scale_percent / 100)
            dim = (width, height)
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
 
            # frame = frame[int(h/5):int(4/5*h),int(w/5):int(4/5*w)]
            # cv2.imshow(f'frame', frame)
            (left,right) = getCoordinates(frame)
            (lcX,lcY) = left
            (rcX,rcY) = right

            print(f"left:{left} right:{right}")
            cv2.circle(sandbox,(int(rcX*512),int(rcY*512)),2,(255,0,0),1)
            cv2.circle(sandbox,(int(lcX*512),int(lcY*512)),2,(0,0,255),1)
            cv2.imshow("sandbox",sandbox)
            
            if cv2.waitKey(1) == ord('q'):
                run = False
                break

    cv2.destroyAllWindows()