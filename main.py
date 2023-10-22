import cv2

#print("Before URL")
cap = cv2.VideoCapture('rtsp://192.168.18.14:8080/h264.sdp')
#print("After URL")

# Load the cascade

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
# Read the input image

def getEyes(gray):
    # Detect faces
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    print(f"{len(eyes)} eyes detected")
    eye_images = []
    for (x, y, w, h) in eyes:
        eye_images.append(gray[y:y+h,x:x+w])
        # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return eye_images


def getFaces(gray):
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    print(f"{len(faces)} faces detected")
    faces_images = []
    for (x, y, w, h) in faces:
        faces_images.append(gray[y:y+h,x:x+w])
        # cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return faces_images

while True:

    #print('About to start the Read command')
    ret, frame = cap.read()
    #print('Running..')
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = getFaces(gray)
    
    for face in faces:
        eyes = getEyes(face)

        for i,eye in enumerate(eyes):
            if i >= 2:
                break
            cv2.imshow(f'eye_{i}', eye)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
