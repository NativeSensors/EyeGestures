import pickle
import platform
import queue
import threading
import sys
import time
import traceback
from string import capwords

import cv2
import numpy as np
import numpy.typing as npt

# Make predictions for new data points


def recoverable(ret_error_params=()):
    def decorator(func):
        """
        timeit
        """

        def inner(*args, **kwargs):
            """
            inner
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Caugh error: {e}")
                return ret_error_params

        return inner

    return decorator


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


def low_pass_filter_fourier(data: npt.NDArray[np.float64], cutoff_frequency: int) -> npt.NDArray[np.float64]:
    # Apply Fourier Transform-based filter column-wise
    filtered_data = np.zeros_like(data, dtype=float)
    for col in range(data.shape[1]):  # Iterate over each column
        fft_data = np.fft.fft(data[:, col])
        frequencies = np.fft.fftfreq(len(data[:, col]))
        # Apply the low-pass filter
        fft_data[np.abs(frequencies) > cutoff_frequency] = 0
        # Perform Inverse Fourier Transform
        filtered_data[:, col] = np.fft.ifft(fft_data).real
    return filtered_data


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
        grid_image = np.zeros((img_h * rows, img_w * cols, images[0].shape[2]), dtype=np.uint8)
    else:
        grid_image = np.zeros((img_h * rows, img_w * cols), dtype=np.uint8)

    # Copy images to the grid
    for i, img in enumerate(images):
        if i >= rows * cols:
            break  # Stop if we have filled the grid
        row = i // cols
        col = i % cols
        grid_image[row * img_h : (row + 1) * img_h, col * img_w : (col + 1) * img_w] = img

    return grid_image


class var:

    def __init__(self, _var):
        self.__var = _var

    def set(self, _var):
        self.__var = _var

    def get(self):
        return self.__var


class Buffor:

    def __init__(self, length):
        self.length = length
        self.__buffor = []

    def add(self, _var):
        if len(self.__buffor) >= self.length:
            self.__buffor.pop(0)

        self.__buffor.append(_var)

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

    def isFull(self):
        return len(self.__buffor) >= self.length

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
            self.t = threading.Thread(target=self.__reader, daemon = True)
            self.t.start()
        else:
            self.frames = []
            with open(name, "rb") as file:
                self.frames = pickle.load(file)

    def __openCam(self, name):
        max_index = 10

        if isinstance(name, int):
            for cam_index in range(name, max_index):
                if "Windows" in platform.system():
                    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(cam_index)

                if cap is None or not cap.isOpened():
                    print(f"Was unable to open camera: {name}.")
                    print(f"Trying to open camera: {name}.")
                    continue

                # testing an actual read
                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.release()
                    continue
                num_black_pixels = np.count_nonzero(frame == 0)
                frame_size = frame.size
                black_pixel_ratio = num_black_pixels / frame_size
                print(frame)
                print(f"black_pixels = {num_black_pixels}, frame_size = {frame_size}")
                print(f"black_pixel_ratio = {black_pixel_ratio}")
                if black_pixel_ratio > 0.9:
                    raise RuntimeError("Camera Frame not captured:")
                print(f"Opened camera: {name}")
                self.cap = cap
                return
            raise RuntimeError("No available camera found or camera busy")
        else:
            cap = cv2.VideoCapture(name)
            if not cap.isOpened():
                raise RuntimeError(f"Unable to open video source:{name}")
            ret, frame = cap.read()
            if not ret:
                cap.release()
                raise RuntimeError("Camera opened but cannot read ( busy camera )")
            num_black_pixels = np.count_nonzero(frame == 0)
            frame_size = frame.size
            black_pixel_ratio = num_black_pixels / frame_size
            print(frame)
            print(f"black_pixels = {num_black_pixels}, frame_size = {frame_size}")
            print(f"black_pixel_ratio = {black_pixel_ratio}")
            if black_pixel_ratio > 0.9:
                raise RuntimeError("Camera Frame not captured:")
            self.cap = cap

    def __reader(self):
        while self.run:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera read failed. Possibly in use or disconnected")
                self.run = False
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

    def read(self, timeout = 2):
        if self.stream:
            try:
                return self.q.get(timeout = timeout)
            except queue.Empty:
                return (False, None)
        if len(self.frames) < 1:
            return (False, None)
        frame = self.frames.pop(0)
        self.frames.pop(0)
        return ((len(self.frames) >= 1), frame)

    def close(self):
        self.run = False
        if self.stream:
            self.t.join()
            if self.cap.isOpened():
                self.cap.release()
