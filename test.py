from appUtils.dot_windows import WindowsCircle, RGBA
from screeninfo import get_monitors
import win32gui, win32ui, win32api, win32con, win32event



monitor = list(filter(lambda monitor: monitor.is_primary == True, get_monitors()))[0]

green = RGBA(0, 100, 0, 128) # green
dot = WindowsCircle(50, 4, green, monitor.width, monitor.height)
dot.show()

for n in range(10000):
    # Check for messages without blocking
    m = win32gui.GetCursorPos()
    dot.show()
    dot.position(m[0], m[1])
    # dot.set_radius(n%100)
