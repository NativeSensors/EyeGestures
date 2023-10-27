import cv2
import dlib
import pickle
import numpy as np
from utils.eyeframes import eyeFrame, eyeFrameStorage

LEFT  = 0
RIGHT = 1

predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class eyeFrame:    

    def __init__(self):
        self.center = (0.0,0.0)
        self.radius = 0.0
        self.leftEye = None
        self.rightEye = None
        self.landmarks = None
        self.faceImg = None

    def setParams(self,faceImg, landmarks, coors):
        (x,y,w,h) = coors
        self.faceImg = faceImg
        self.landmarks = landmarks
        self.coors = coors

        self.leftEye  = faceSquare[:int(w/2),int(h/2):]
        self.rightEye = faceSquare[:int(w/2),:int(h/2)]        

        self.center = (x+int(w/2),y+int(h/2))
        self.radius = int(w/4)

        pass

    def getCenter(self):
        return self.center

    def getRadius(self):
        return self.radius

    def getCoors(self):
        return self.coors

    def getFaceImg(self):
        return self.faceImg

    def getLandMarks(self):
        return self.landmarks

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
        
        eFrame.setParams(faceSquare, landmarks, (x, y, w, h))
        left_eye_region  = faceSquare[:int(w/2),int(h/2):]
        right_eye_region = faceSquare[:int(w/2),:int(h/2)]        

        
        for landmark in landmarks:
            # print(/,landmark)
            image = cv2.circle(image, (landmark[0],landmark[1]), 1, (0, 0, 255), 1) 
            
        image = cv2.rectangle(image, (x,y), (x+w,y+h), (255, 0, 0), 2) 
        image = cv2.rectangle(image, (x,y), (x+int(w/2),y+int(h/2)), (0, 0, 255), 2) 
        image = cv2.rectangle(image, (x+int(w/2),y), (x+w,y+int(h/2)), (0, 255, 0), 2) 
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), 5, (0, 255, 255), 5) 
        image = cv2.circle(image, (x+int(w/2),y+int(h/2)), int(w/4), (0, 255, 255), 1) 
        # cv2.imshow(f'faceSquare', faceSquare)
        # cv2.imshow(f'left_eye_region', left_eye_region)
        # cv2.imshow(f'right_eye_region', right_eye_region)
        
        # left_eye  = getEye(left_eye_region  , eye_cascade.detectMultiScale(left_eye_region, 1.1, 4))
        # right_eye = getEye(right_eye_region , eye_cascade.detectMultiScale(right_eye_region, 1.1, 4))

        # left_eye_landmarks = landmarks[LEFT_EYE_KEYPOINTS,:]
        # left_eye_landmarks = landmarks[RIGHT_EYE_KEYPOINTS,:]

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
            
            if cv2.waitKey(1) == ord('q'):
                run = False
                break

    cv2.destroyAllWindows()