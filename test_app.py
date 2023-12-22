import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import pyautogui
import threading
from appUtils.dot_windows import WindowsCursor 

if __name__ == "__main__":
    new_cursor = WindowsCursor(50,2)

    for n in range(100000):
        print(n)
        x, y = pyautogui.position()
        new_cursor.set_radius(n%20 + 1)
        new_cursor.move(x,y)

    new_cursor.close_event()
