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

def getEyes(image):
    LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for faceSquare, landmarks, (x, y, w, h) in getFace(gray):
        eFrame = eyeFrame()
        eFrame.setParams(gray,faceSquare, landmarks, (x, y, w, h))
        tracker.update(eFrame)

        sink = EyeSink()
        
        left_eye_region  = eFrame.getLeftEye()
        right_eye_region = eFrame.getRightEye()

        left_eye_show = cv2.cvtColor(left_eye_region,cv2.COLOR_GRAY2RGB)
        right_eye_show = cv2.cvtColor(right_eye_region,cv2.COLOR_GRAY2RGB)

        cv2.imshow("left_eye", left_eye_region)
        (cX,cY) = sink.push(left_eye_region)
        
        if cX != 0 or cY != 0:
            cv2.circle(left_eye_show , (cX,cY), 2, (0, 0, 255), -1)
        
        (cX,cY) = sink.push(right_eye_region)
        if cX != 0 or cY != 0:
            cv2.circle(right_eye_show , (cX,cY), 2, (255, 0, 0), -1)
            
        # put text and highlight the center

        cv2.imshow("left_eye", left_eye_show )
        cv2.imshow("right_eye", right_eye_show)

        # rx,ry = x+int(w/2),y    
        # for eye_right in eyes_right:
        #     (x,y,w,h) = eye_right
        #     image = cv2.rectangle(image, (x,y), (x+w,y+h), (255, 0, 0), 2) 
    
    eFrame = tracker.getFrame().addFeaturesToImg(image)
    cv2.imshow(f'image', image)
        


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords


if __name__ == "__main__":
    frames = []
    run = True

    with open('recording/data27-10-2023-16:17:31.pkl', 'rb') as file:
        frames = pickle.load(file)

    while run:
        for n, frame in enumerate(frames):
            w = frame.shape[0]
            h = frame.shape[1]
            frame = frame[int(h/5):int(4/5*h),int(w/5):int(4/5*w)]
            # cv2.imshow(f'frame', frame)
            getEyes(frame)
            
            if cv2.waitKey(10) == ord('q'):
                run = False
                break

    cv2.destroyAllWindows()