import cv2
from eyeGestures.utils import VideoCapture
from eyeGestures.face import FaceFinder

def showEyes(image,face):

    if face is not None:
        cv2.circle(frame,face.getLeftPupil(),2,(0,0,255),1)
        for point in face.getLeftEye():
            cv2.circle(frame,point,2,(0,255,0),1)

        cv2.circle(frame,face.getRightPupil(),2,(0,0,255),1)
        for point in face.getRightEye():
            cv2.circle(frame,point,2,(0,255,0),1)


if __name__ == "__main__":    
    vid = VideoCapture('recording/calibrationData1.pkl')
    # vid = VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
    
    faceFinder = FaceFinder()

    # use half of the data for fitting
    pFrame = None
    flow = None
    ret = True
    while ret:
        
        ret, frame = vid.read()
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        # detect face 
        face = faceFinder.find(gray)
        
        #display face
        showEyes(frame,face)
        cv2.imshow("frame",frame)
    
        if cv2.waitKey(10) == ord('q'):
            run = False
            break         

    cv2.destroyAllWindows()