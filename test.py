import win32api
import win32con
import win32gui
import win32ui
import win32event
import win32process
from PySide2.QtGui import QColor

def create_cursor(color, radius):
    # Create a window to attach the cursor to
    hwnd = win32gui.GetDesktopWindow()
    dc = win32gui.GetDC(hwnd)

    # Create a memory DC
    mem_dc = win32ui.CreateDCFromHandle(dc)
    mem_dc.CreateCompatibleDC()

    # Create a bitmap
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mem_dc, radius * 2, radius * 2)

    # Select the bitmap into the memory DC
    mem_dc.SelectObject(bmp)

    # Draw a transparent circle on the bitmap
    mem_dc.SetBkMode(win32con.TRANSPARENT)
    brush = win32ui.CreateBrush(1, 0)  # 1: BS_SOLID, 0: TRANSPARENT
    mem_dc.SelectObject(brush)

    pen = win32ui.CreatePen(0, 1, 0)  # 0: PS_SOLID, 1: pen width
    mem_dc.SelectObject(pen)

    mem_dc.Ellipse((0, 0, radius * 2, radius * 2))

    # Release resources
    win32gui.ReleaseDC(hwnd, dc)

    # Create a cursor from the bitmap
    cursor_info = win32gui.GetIconInfo(bmp.GetHandle())
    cursor = win32gui.CreateIconIndirect(cursor_info[4])

    return cursor

def set_custom_cursor(cursor):
    # Set the cursor
    win32gui.SetSystemCursor(cursor, win32con.OCR_NORMAL)

def main():
    # Specify the color and radius of the circular cursor
    cursor_color = QColor(255, 0, 0, 128)  # Red color with 50% transparency
    cursor_radius = 20

    # Create a circular semi-transparent cursor
    cursor = create_cursor(cursor_color, cursor_radius)

    # Set the custom cursor
    set_custom_cursor(cursor)

    # Run the application (you can add your own event loop or use PyQt, etc.)
    win32event.WaitForSingleObject(win32process.GetCurrentProcess(), win32event.INFINITE)

if __name__ == "__main__":
    main()
