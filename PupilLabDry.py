from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures
from screeninfo import get_monitors

if __name__ == '__main__':
    eye_screen_w = 500
    eye_screen_h = 500
    gestures = EyeGestures(eye_screen_w,
                           eye_screen_h,
                           250,
                           250)
    
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

        

