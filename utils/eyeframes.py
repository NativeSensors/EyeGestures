
class eyeFrame:
    def __init__(self,eyes,eyes_landmarks):
        self.eyes = eyes
        self.eyes_landmarks = eyes_landmarks

    def get(self):
        return self.eyes

class eyeFrameStorage:
    def __init__(self):
        self.frames = []

    def append(self,frame):
        self.frames.append(frame)

    def get(self):
        return self.frame