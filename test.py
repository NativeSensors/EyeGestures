import win32gui, win32ui, win32api, win32con, win32event
import math
import time
import pygetwindow as gw
from screeninfo import get_monitors

class WindowsCircle:

    def __init__(self, radius, thickness, color, width, height):
        self.color = color
        self.radius = radius
        self.thickness = thickness

        self.dc = win32gui.GetDC(0)
        self.dcObj = win32ui.CreateDCFromHandle(self.dc)
        self.hwnd = win32gui.GetDesktopWindow()
        self.monitor = (0, 0, width, height)
        self.width = width
        self.height = height
        self.past_coordinates = self.monitor
        self.prev_frame = []
        self.x = 0
        self.y = 0

        self.buffer_dc = self.dcObj.CreateCompatibleDC()
        self.buffer_bitmap = win32ui.CreateBitmap()
        self.buffer_bitmap.CreateCompatibleBitmap(self.dcObj, self.width, self.height)
        self.buffer_dc.SelectObject(self.buffer_bitmap)
        self.buffer_dc.SetBkColor(win32api.RGB(255, 255, 255))  # Set background color to white

        self.event = win32event.CreateEvent(None, 0, 0, None)

    def getHwnd(self):
        return self.hwnd

    def position(self, x, y):
        self.x = x
        self.y = y

    def __refresh(self):
        # clean previous frame
        win32gui.BitBlt(self.dc, self.past_coordinates[0], self.past_coordinates[1], self.past_coordinates[2] + 10, self.past_coordinates[3] + 10, self.buffer_dc.GetSafeHdc(), 0, 0, win32con.SRCCOPY)

        width = height = self.radius *2

        # capture new bitmap for reference
        src_dc = win32gui.GetDC(0)
        win32gui.BitBlt(self.buffer_dc.GetSafeHdc(), 0, 0, width + 10, height + 10 , src_dc, self.x - self.radius , self.y - self.radius , win32con.SRCCOPY)
        win32gui.ReleaseDC(0, src_dc)

    def __draw(self):
        width = height = self.radius *2
        # Draw the circles on the buffer
        for thick in range(self.thickness):
            for angle in range(0, 360):
                angle_rad = angle * 3.14159 / 180.0
                r = max(self.radius - thick, 0)
                x_pixel = int(self.x + r * math.cos(angle_rad))
                y_pixel = int(self.y + r * math.sin(angle_rad))
                x_pixel = max(x_pixel, 0)
                y_pixel = max(y_pixel, 0)
                x_pixel = min(x_pixel, self.width - 1)
                y_pixel = min(y_pixel, self.height - 1)

                win32gui.SetPixel(self.dc, x_pixel, y_pixel, self.color)

        self.past_coordinates = (self.x - self.radius, self.y - self.radius, width , height )


    def _on_timer(self):
        # Draw the background from the buffer
        self.__refresh()
        self.__draw()
        time.sleep(10/1000)

    def show(self):
        self._on_timer()

def RGBA(r, g, b, a):
    # Ensure that the values are in the valid range (0-255)
    r = max(0, min(r, 255))
    g = max(0, min(g, 255))
    b = max(0, min(b, 255))
    a = max(0, min(a, 255))

    # Create the RGBA color
    color = win32api.RGB(r, g, b)

    # Shift the alpha value to the appropriate position
    color |= a << 24

    return color


monitor = list(filter(lambda monitor: monitor.is_primary == True, get_monitors()))[0]

green = RGBA(0, 100, 0, 128) # green
dot = WindowsCircle(50, 2, green, monitor.width, monitor.height)

dot.show()

for n in range(10000):
    # Check for messages without blocking
    m = win32gui.GetCursorPos()
    dot.position(m[0], m[1])
    dot.show()
