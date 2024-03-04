import cv2
from eyeGestures.eyegestures import EyeGestures
from screeninfo import get_monitors

if __name__ == '__main__':
    eye_screen_w = 500
    eye_screen_h = 500
    gestures = EyeGestures(eye_screen_w,
                           eye_screen_h,
                           250,
                           250)
    
    # Load an image from file
    face_1_img = cv2.imread('test_data/face_1.jpg')
    face_2_img = cv2.imread('test_data/face_2.jpg')

    prev_point = [0,0]
    for n in range(50):
      
        monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        event = gestures.estimate(
            face_1_img,
            "main_1",
            monitor.width,
            monitor.height,
            monitor.x,
            monitor.y,
            0.8)

        print(event.point,event.fixation)
        if(prev_point[0] == 0.0):
            prev_point = event.point

        if(prev_point[0] != event.point[0] or prev_point[1] != event.point[1]):
            print("FAILED")

        prev_point = event.point

    print("\033[92m=================================================\033[0m")
    prev_point = [0,0]
    for n in range(50):
            
        monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        event = gestures.estimate(
            face_2_img,
            "main_2",
            monitor.width,
            monitor.height,
            monitor.x,
            monitor.y,
            0.8)

        print(event.point,event.fixation)
        if(prev_point[0] == 0.0):
            prev_point = event.point

        if(prev_point[0] != event.point[0] or prev_point[1] != event.point[1]):
            print("\033[91m>>>>>>>>>>>>>>>>>>>>>> FAILED <<<<<<<<<<<<<<<<<<<<<<<<\033[0m")

        prev_point = event.point

    print("\033[92m=================================================\033[0m")
    prev_point = [0,0]
    for n in range(25):
            
        monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        event = gestures.estimate(
            face_2_img,
            "main_2",
            monitor.width,
            monitor.height,
            monitor.x,
            monitor.y,
            0.8,
            1)
            
        print(event.point,event.fixation)
        
        monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        event = gestures.estimate(
            face_1_img,
            "main_1",
            monitor.width,
            monitor.height,
            monitor.x,
            monitor.y,
            0.8,
            1)
            

        print(event.point,event.fixation)
    # for n in range(50):
      
    #     monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
    #     event = gestures.estimate(
    #         face_1_img,
    #         "main_1",
    #         monitor.width,
    #         monitor.height,
    #         monitor.x,
    #         monitor.y,
    #         0.8)

    #     print(event.point)
            
    #     monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
    #     event = gestures.estimate(
    #         face_2_img,
    #         "main_2",
    #         monitor.width,
    #         monitor.height,
    #         monitor.x,
    #         monitor.y,
    #         0.8)

    #     print(event.point)

