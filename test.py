import cv2
import math
import numpy as np
import mediapipe as mp
import pyautogui

cam = cv2.VideoCapture('rtsp://192.168.18.30:8080/h264.sdp')
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

def find_normal_vector(points):
    # Assuming points are 3D
    # Calculate two vectors that lie on the plane
    vec1 = points[1] - points[0]
    vec2 = points[2] - points[0]

    # Calculate the normal vector (cross product)
    normal = np.cross(vec1, vec2)
    return normal / np.linalg.norm(normal)  # Normalize the vector


def find_center(points):
    print(points)
    return np.mean(points, axis=0)

def project_to_2d(point, focal_length=1):
    # Simple perspective projection
    x, y, z = point
    return np.array([focal_length * (x / z), focal_length * (y / z)])


while True:
    _, frame = cam.read()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    if landmark_points:
        landmarks = landmark_points[0].landmark
        (pupil,p1,p2,p3,p4) = landmarks[473:478]
        

        eyeIndicies = [263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]
        eyeLandmarks = [landmarks[i] for i in eyeIndicies]
        points = np.array([(pupil.x,pupil.y,pupil.z),(p1.x,p1.y,p1.z),(p2.x,p2.y,p1.z),(p3.x,p3.y,p1.z),(p4.x,p4.y,p1.z)])
        center_3d = np.array((pupil.x,pupil.y,pupil.z))
        center_2d = np.array([center_3d[0],center_3d[1]])
        center_2d[0] = center_2d[0] * frame_w
        center_2d[1] = center_2d[1] * frame_h

        SumX = 0
        SumY = 0

        for id, landmark in enumerate(eyeLandmarks):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h) 
            cv2.circle(frame, (x, y), 1, (0, 255, 0),-1)

            SumX += (x - center_2d[0])
            SumY += (y - center_2d[1])

        for id, landmark in enumerate(landmarks[473:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h) 
            cv2.circle(frame, (x, y), 1, (0, 0, 255),-1)

        gaze_vector = np.array([-SumX,SumY])

        print(center_2d,gaze_vector)
    
        # Draw the gaze vector
        cv2.arrowedLine(frame, tuple(center_2d.astype(int)), tuple((center_2d + gaze_vector).astype(int)), (0, 255, 0), 2)
        
        cv2.circle(frame,tuple(center_2d.astype(int)), 1, (0, 0, 255),-1)


    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
