import cv2
import time
import pickle 

#print("Before URL")
cap = cv2.VideoCapture('rtsp://192.168.18.14:8080/h264.sdp')
#print("After URL")

# Load the cascade

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
# Read the input image

class eyeFrame:
    def __init__(self,eyes):
        self.eyes = eyes

    def get(self):
        return self.eyes

class eyeFrameStorage:
    def __init__(self):
        self.frame = []

    def append(self,frame):
        self.frame.append(frame)

    def get(self):
        return self.frame

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
    faces_images = []
    for (x, y, w, h) in faces:
        faces_images.append(gray[y:y+h,x:x+w])
        # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return faces_images

framesStorage = eyeFrameStorage()

if __name__ == "__main__":

    # Get the current time
    while True:

        #print('About to start the Read command')
        ret, frame = cap.read()
        #print('Running..')
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = getFaces(gray)
        
        if len(faces) > 0:
            
            face = faces[0]
        
            left_face = face[:int(face.shape[0]/2),:int(face.shape[0]/2)]
            right_face = face[:int(face.shape[0]/2),int(face.shape[0]/2):]
            leftEye = eyeFrame(getEyes(left_face))
            rightEye = eyeFrame(getEyes(right_face))

            if len(leftEye.get()) > 0:
                cv2.imshow(f'left_eye', leftEye.get()[0])
            
            if len(rightEye.get()) > 0:    
                cv2.imshow(f'right_eye', rightEye.get()[0])

            if cv2.waitKey(1) == ord('q'):
                break

    with open(f'recording/data{time.time()}.pkl', 'wb') as file:
        pickle.dump(framesStorage, file)

    cap.release()
    cv2.destroyAllWindows()
