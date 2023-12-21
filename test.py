import win32gui, win32ui, win32api, win32con
from win32api import GetSystemMetrics
import math

dc = win32gui.GetDC(0)
dcObj = win32ui.CreateDCFromHandle(dc)
hwnd = win32gui.WindowFromPoint((0,0))
monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

red = win32api.RGB(255, 0, 0)  # Red

past_coordinates = monitor
while True:
    m = win32gui.GetCursorPos()

    # Create a circular region (using a large radius to approximate a circle)
    radius = 60
    rect = win32gui.CreateRoundRectRgn(m[0] - radius, m[1] - radius, m[0] + radius, m[1] + radius, radius * 2, radius * 2)

    # Redraw the circular region
    win32gui.RedrawWindow(hwnd, past_coordinates, rect, win32con.RDW_INVALIDATE)

    # Draw a circle
    for angle in range(0, 360):
        angle_rad = angle * 3.14159 / 180.0
        x_pixel = int(m[0] + radius * math.cos(angle_rad))
        y_pixel = int(m[1] + radius * math.sin(angle_rad))
        print(dc,x_pixel, y_pixel, red,m)
        win32gui.SetPixel(dc, x_pixel, y_pixel, red)

    past_coordinates = (m[0] - radius, m[1] - radius, m[0] + radius, m[1] + radius)
