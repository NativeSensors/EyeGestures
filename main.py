import cv2
import pickle

class eyeFrame:
    def __init__(self,eyes):
        self.eyes = eyes

    def get(self):
        return self.eyes

class eyeFrameStorage:
    def __init__(self):
        self.frame = []

    def append(self,frame):
        self.frame.append()

    def get(self):
        return self.frame


if __name__ == "__main__":
    framesStorage = eyeFrameStorage()

    with open('recording/data.pkl', 'rb') as file:
        framesStorage = pickle.load(file)

    for n, frame in enumerate(framesStorage.get()):

        for i,eye in enumerate(frame.get()):
            cv2.imshow(f'eye_{i}', eye)

        if cv2.waitKey(10) == ord('q'):
            break

    cv2.destroyAllWindows()