import time
import queue
import pickle
import platform
import threading

import cv2
import numpy as np

# Make predictions for new data points


def timeit(func):
    """
    timeit
    """
    def inner(*args, **kwargs):
        """
        inner
        """
        start = time.time()
        ret = func(*args, **kwargs)
        print(f"Elapsed time: {time.time() - start}")
        return ret
    return inner


def shape_to_np(shape, dtype="int"):
    """
    shape_to_np
    """
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
        grid_image = np.zeros(
            (img_h * rows, img_w * cols, images[0].shape[2]), dtype=np.uint8)
    else:
        grid_image = np.zeros((img_h * rows, img_w * cols), dtype=np.uint8)

    # Copy images to the grid
    for i, img in enumerate(images):
        if i >= rows * cols:
            break  # Stop if we have filled the grid
        row = i // cols
        col = i % cols
        grid_image[row * img_h:(row + 1) * img_h, col *
                   img_w:(col + 1) * img_w] = img

    return grid_image


class var:

    def __init__(self, var):
        self.__var = var

    def set(self, var):
        self.__var = var

    def get(self):
        return self.__var


class Buffor:

    def __init__(self, length):
        self.length = length
        self.__buffor = []

    def add(self, var):
        if len(self.__buffor) >= self.length:
            self.__buffor.pop(0)

        self.__buffor.append(var)

    def getAvg(self, lenght=0):
        return np.sum(self.__buffor[-lenght:], axis=0) / len(self.__buffor[-lenght:])

    def getBuffor(self):
        return self.__buffor

    def loadBuffor(self, buffor):
        self.__buffor = buffor

    def getLast(self):
        return self.__buffor[0]

    def getFirst(self):
        return self.__buffor[len(self.__buffor) - 1]

    def getLen(self):
        return len(self.__buffor)
    
    def flush(self):
        tmp = self.__buffor[-1]
        self.__buffor = []
        self.__buffor.append(tmp)

    def clear(self):
        self.__buffor = []

# Bufforless


class VideoCapture:
    """Wrapper on openCV2 stream making it bufforless and adding camera search"""

    def __init__(self, name, bufforless=True):
        self.bufforless = bufforless
        self.run = True

        if isinstance(name, str):
            if ".pkl" in name:
                self.stream = False
            else:
                self.stream = True
        else:
            self.stream = True

        if self.stream:
            self.prev_frame = None

            self.__openCam(name)

            self.q = queue.Queue()
            self.t = threading.Thread(target=self.__reader)
            self.t.start()
        else:
            self.frames = []
            with open(name, 'rb') as file:
                self.frames = pickle.load(file)

    def __openCam(self, name):
        if isinstance(name, int):
            if "Windows" in platform.system():
                self.cap = cv2.VideoCapture(name, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(name)

            if self.cap is None or not self.cap.isOpened():
                print(f"Was unable to open camera: {name}.")
                print(f"Trying to open camera: {name}.")
                if name + 1 < 10:
                    self.__openCam(name + 1)
        else:
            self.cap = cv2.VideoCapture(name)

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
            self.q.put((ret, frame))

        self.flush()

    def flush(self):
        while not self.q.empty():
            self.q.get()

    def read(self):
        """Function returning latest frame"""
        if self.stream:
            return self.q.get()
        else:
            frame = self.frames.pop(0)
            self.frames.pop(0)
            return ((len(self.frames) >= 1), frame)

    def close(self):
        """Function closing stream"""
        self.run = False
        self.t.join()
        self.cap.release()
