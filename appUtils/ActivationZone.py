

import sys
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton
from PySide2.QtCore import Qt, QTimer, QRect, QPoint
from PySide2.QtGui import QTransform
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from screeninfo import get_monitors
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import threading
import platform

class RegionOfInterest(QWidget):

    def __init__(self, parent=None):
        super().__init__()

        self.x = 0
        self.y = 0
        self.width = 1000
        self.height= 1000

        # Set up the window attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.root = None
        self.t = threading.Thread(target=self.__create)
        self.t.start()

    def __create_transparent_rectangle_with_semi_transparent_circle(self, size):
        # Create a transparent rectangle image with a semi-transparent orange circle in the middle
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw the transparent rectangle
        draw.rectangle([(0, 0), size], fill="black")

        # Draw the semi-transparent orange circle in the middle
        circle_radius = self.circle_radius1
        circle_center = (size[0] // 2, size[1] // 2)
        draw.ellipse([(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
                    (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
                    fill="orange")  # Use (R, G, B, A) for the color, where A is the alpha (transparency)

        circle_radius = self.circle_radius2
        draw.ellipse([(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
                    (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
                    fill=(0, 0, 0, 256))  # Use (R, G, B, A) for the color, where A is the alpha (transparency)

        return image


    def __create(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)  # Set the window to always be on top

        # Set rectangular window shape
        self.root.geometry(f"{self.width}x{self.height}")
        self.circle_radius1 = self.radius
        self.circle_radius2 = self.radius - 1
        self.image = self.__create_transparent_rectangle_with_semi_transparent_circle((self.width, self.height))
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Create a label with the image as a background
        self.label = tk.Label(self.root, image=self.tk_image)
        self.label.pack(fill="both", expand=True)

        # Set transparency
        if "Windows" in platform.system():
            self.root.attributes("-transparentcolor", "black")
        # Schedule the update of the window position
        self.root.after(10, lambda: self.__update_window_position(self.root))

        self.root.mainloop()


    def disappear(self):
        self.hide()

    def close_event(self):
        self.close()

    def show_again(self):
        pass
        # self.setStyleSheet("background-color: #de4dff00; border-radius: 10px;")

    def set_new_position(self,x,y):
        self.x = x
        self.y = y
        self.move(self.x, self.y)

    def set_new_width(self,x,y):
        self.x = x
        self.y = y
        self.setGeometry(self.x, self.y, self.width, self.height)

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        print("calling mouse event")
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        print("calling mouse event")
        self.end = event.pos()
        self.update()

    # def mouseReleaseEvent(self, event):
    #     print("mouseReleaseEvent")
    #     self.begin = event.pos()
    #     self.end = event.pos()
    #     self.update()


class AceeptRemoveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.x = 0
        self.y = 0

        # Set up the window attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = QHBoxLayout(self)
        layout.setSpacing(0)

        # Create Accept button with checkmark icon
        draw_button = QPushButton(QtGui.QIcon.fromTheme("dialog-ok-apply"), "⏹")
        draw_button.setStyleSheet(
            """
            QPushButton {
                padding: 0px; margin: 0px; width: 50px; height: 50px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                border: 2px solid #16171f;
                border-right: none;
                border-left: none;
                background: #1d1e27;
            }
            QPushButton:hover {
                background: #0062ff; /* Change border color on hover */
            }
            """)  # Remove padding and margin
        layout.addWidget(draw_button)

        # Create Accept button with checkmark icon
        accept_button = QPushButton(QtGui.QIcon.fromTheme("dialog-ok-apply"), "✔️")
        accept_button.setStyleSheet(
            """
            QPushButton {
                padding: 0px; margin: 0px; width: 50px; height: 50px;
                border: 2px solid #16171f;
                color: green;
                border-right: none;
                border-left: none;
                background: #1d1e27;
            }
            QPushButton:hover {
                background: #0062ff; /* Change border color on hover */
            }
            """)  # Remove padding and margin
        layout.addWidget(accept_button)

        # Create Close button with close icon
        close_button = QPushButton(QtGui.QIcon.fromTheme("dialog-close"), "❌")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(
            """
            QPushButton {
                padding: 0px; margin: 0px; width: 50px; height: 50px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                border: 2px solid #16171f;
                color: red;
                border-left: none;
                background: #1d1e27;
            }
            QPushButton:hover {
                background: #0062ff; /* Change border color on hover */
            }
            """)  # Remove padding and margin
        layout.addWidget(close_button)

def rectangle_class(self):
    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
        """
        Draw a rounded rectangle on Tkinter Canvas.
        Parameters:
        - canvas: Tkinter Canvas object
        - x1, y1: Coordinates of the top left corner
        - x2, y2: Coordinates of the bottom right corner
        - radius: Radius of the rounded corners
        - kwargs: Additional arguments for canvas.create_polygon()
        """
        points = [x1+radius, y1,
                x1+radius, y1, x2-radius, y1, x2-radius, y1,
                x2, y1, x2, y1+radius,
                x2, y1+radius, x2, y2-radius, x2, y2-radius,
                x2, y2, x2-radius, y2,
                x2-radius, y2, x1+radius, y2, x1+radius, y2,
                x1, y2, x1, y2-radius,
                x1, y2-radius, x1, y1+radius, x1, y1+radius,
                x1, y1]

        # Create rounded corners
        canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2, start=90, extent=90, style="pieslice", outline="", **kwargs)
        canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2, start=0, extent=90, style="pieslice", outline="", **kwargs)
        canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2, start=270, extent=90, style="pieslice", outline="", **kwargs)
        canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2, start=180, extent=90, style="pieslice", outline="", **kwargs)

        # Create the rectangle
        canvas.create_polygon(points, **kwargs, smooth=True)

    root = tk.Tk()
    root.overrideredirect(True)
    monitor = get_monitors()[0]
    root.title("Rounded Rectangle")
    root.attributes("-alpha", 0.5)
    root.attributes("-transparentcolor","white")

    canvas = tk.Canvas(root, width=monitor.width-5, height=monitor.height-5, bg="white")
    canvas.pack(fill="both", expand=True)

    create_rounded_rectangle(canvas, 50, 50, 350, 250, 20, fill="lightblue")

    root.after(500, root.destroy)
    root.mainloop()




if __name__ == '__main__':

    app = QApplication(sys.argv)
    accept_remove = AceeptRemoveWidget()
    accept_remove.show()

    sys.exit(app.exec_())
