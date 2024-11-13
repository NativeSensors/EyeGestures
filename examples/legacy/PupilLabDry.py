from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from screeninfo import get_monitors

if __name__ == '__main__':
    gestures = EyeGestures(285,115)
    
    cap = VideoCapture(0)
    
    while True:

        ret, frame = cap.read()     
            
        monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        event = gestures.estimate(
            frame,
            "main",
            monitor.width,
            monitor.height,
            monitor.x,
            monitor.y,
            0.8)

        

