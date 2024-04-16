
from pathlib import Path

import threading
import pyautogui
import datetime
import pickle
import queue
import time
import csv
import os

class DataManager:

    def __init__(self):
        self.number_of_csv = 0
        self.sizes = [0]
        self.ipc = queue.Queue()
        self.screenshots_enable = False

    def enable_screenshots(self):
        if not self.screenshots_enable:
            self.screenshots_enable = True
            t = threading.Thread(target=self.__save_screenshots)
            t.start()
            print("screenshots enabled")

    def disable_screenshots(self):
        self.screenshots_enable = False

    def __send_screenshot(self, filename):
        self.ipc.put(filename)

    def __save_screenshots(self):
        fps_cap = 1
        start = time.time()
        screenshot = pyautogui.screenshot()
        while self.screenshots_enable:
            if self.ipc.not_empty:
                try:
                    filename = self.ipc.get(True,1.0)
                    if (time.time() - start) > 1.0/fps_cap:
                        screenshot = pyautogui.screenshot()
                        # Define the desired width and height for the resized image
                        desired_width = 800
                        desired_height = 600
                        # Resize the screenshot
                        screenshot = screenshot.resize((desired_width, desired_height))
                    screenshot.save(filename)
                except:
                    print("no item available")
        print("exiting saving")

    def add_frame(self,directory,gevent,rois_to_save):
        timestamp = datetime.datetime.now().timestamp()

        Path(f"./data/{directory}").mkdir(parents=True, exist_ok=True)
        Path(f"./data/{directory}/recordings").mkdir(parents=True, exist_ok=True)


        headers = ["unix_timestamp","point_x", "point_y", "blink", "fixation",
                "screen_x", "screen_y", "screen_width", "screen_height",
                "l_eye_landmarks", "r_eye_landmarks", "l_eye_pupil", "r_eye_pupil","rois"]

        if self.sizes[self.number_of_csv] > 100:
            self.number_of_csv += 1
            self.sizes.append(0)

        filename = f"./data/{directory}/data_{self.number_of_csv}.csv"
        write_headers = not os.path.exists(filename)
        append = os.path.exists(filename)

        with open(filename, 'a' if append else 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if write_headers:
                writer.writerow(headers)

            # Extract data during saving
            point_x, point_y = gevent.point
            screen_x, screen_y = gevent.point_screen
            l_eye_landmarks = gevent.l_eye.getLandmarks()  # Assuming get_landmarks() returns landmarks
            r_eye_landmarks = gevent.r_eye.getLandmarks()  # Assuming get_landmarks() returns landmarks
            l_eye_pupil = gevent.l_eye.getPupil()        # Assuming get_pupils() returns pupils
            r_eye_pupil = gevent.r_eye.getPupil()        # Assuming get_pupils() returns pupils
            screen_width = gevent.screen_man.width
            screen_height = gevent.screen_man.height

            row = [timestamp,
                point_x, point_y, gevent.blink, gevent.fixation,
                screen_x, screen_y,
                screen_width, screen_height,
                pickle.dumps(l_eye_landmarks),
                pickle.dumps(r_eye_landmarks),
                pickle.dumps(l_eye_pupil),
                pickle.dumps(r_eye_pupil),
                rois_to_save]

            writer.writerow(row)
            self.sizes[self.number_of_csv] += 1

        if self.screenshots_enable:
            img_filename = f'{timestamp}.png'
            img_filepath = f"./data/{directory}/recordings"
            self.make_screenshot(img_filepath,img_filename)


    def make_screenshot(self,path,name):
        img_filepath = f"{path}/{name}"

        self.__send_screenshot(img_filepath)