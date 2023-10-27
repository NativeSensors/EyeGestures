import cv2
import pickle 
import numpy as np
from datetime import datetime
from utils.eyeframes import eyeFrame, eyeFrameStorage
import cv2
import dlib

if __name__ == "__main__":
    #print("Before URL")
    cap = cv2.VideoCapture('rtsp://192.168.18.14:8080/h264.sdp')
    #print("After URL")

    frames = []
    # Get the current time
    while True:
        
        #print('About to start the Read command')
        ret, frame = cap.read()
        frames.append(frame)

        cv2.imshow("frame",frame)
        if cv2.waitKey(1) == ord('q'):
            break


    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H:%M:%S")

    with open(f'recording/data{dt_string}.pkl', 'wb') as file:
        pickle.dump(frames, file)

    cap.release()
    cv2.destroyAllWindows()
