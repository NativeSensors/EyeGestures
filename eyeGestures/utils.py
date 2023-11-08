import cv2
import dlib
import time
import pickle
import pyautogui
import numpy as np
from typing import Callable, Tuple
import numpy as np
import queue
import threading

# Make predictions for new data points
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def make_image_grid(images, rows, cols):
    """
    Make a grid of images.

    Parameters:
    - images: list of images to form the grid (all images must be of the same size and type)
    - rows, cols: number of rows and columns in the grid

    Returns:
    - grid_image: image grid as a single image
    """
    # Check if the list of images is not empty and that we have enough to fill the grid
    assert images, "List of images is empty"
    # assert len(images) >= rows * cols, "Not enough images to fill the grid"

    # Get image dimensions
    img_h, img_w = images[0].shape[:2] 
    
    if len(images[0].shape) > 2:
        # Create a black canvas to draw the grid on
        grid_image = np.zeros((img_h * rows, img_w * cols, images[0].shape[2]), dtype=np.uint8)
    else:
        grid_image = np.zeros((img_h * rows, img_w * cols), dtype=np.uint8)

    # Copy images to the grid
    for i, img in enumerate(images):
        if i >= rows * cols:
            break  # Stop if we have filled the grid
        row = i // cols
        col = i % cols
        grid_image[row * img_h:(row + 1) * img_h, col * img_w:(col + 1) * img_w] = img

    return grid_image


class var:

    def __init__(self,var):
        self.__var = var

    def set(self,var):
        self.__var = var

    def get(self):
        return self.__var


# Bufforless
class VideoCapture:

    def __init__(self,name,bufforless = True):
        self.bufforless = bufforless
        self.run = True
        
        if ".pkl" in name:
            self.stream = False
        else:
            self.stream = True
        
        if self.stream: 
            self.prev_frame = None
            self.cap = cv2.VideoCapture(name)
            self.q = queue.Queue()
            self.t = threading.Thread(target=self.__reader).start()
        else:
            self.frames = []
            with open(name, 'rb') as file:
                self.frames = pickle.load(file)

    def __reader(self):
        while self.run:
            ret, frame = self.cap.read()
            if not ret:
                break 
            if not self.q.empty() and self.bufforless:
                try: 
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put((ret,frame))
        
        self.run = False

    def read(self):
        if self.stream:
            return self.q.get()
        else:
            frame = self.frames.pop(0)
            self.frames.pop(0)
            return ((len(self.frames) > 1), frame)

