import cv2
import pickle
import numpy as np
from utils.eyeframes import eyeFrame, eyeFrameStorage

LEFT  = 0
RIGHT = 1

if __name__ == "__main__":
    framesStorage = eyeFrameStorage()

    with open('recording/data1698342309.233691.pkl', 'rb') as file:
        framesStorage = pickle.load(file)

    prev_left_eye = None
    prev_right_eye = None
    while True:
        for n, frame in enumerate(framesStorage.get()):
            print(f"n: {n}")
            
            if not isinstance(prev_left_eye, np.ndarray) and not isinstance(prev_right_eye, np.ndarray):
                prev_left_eye = frame[LEFT].get()[0]
                prev_right_eye= frame[RIGHT].get()[0]

            if len(frame) > 1:
                print(frame[LEFT].get(),frame[RIGHT].get())
                if(len(frame[LEFT].get()) > 1):
                    left_eye  = frame[LEFT].get()[0]
                    right_eye = frame[RIGHT].get()[0]

                    cv2.imshow(f'left_eye', left_eye)
                    cv2.imshow(f'right_eye', right_eye)

            if cv2.waitKey(1) == ord('q'):
                break

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()