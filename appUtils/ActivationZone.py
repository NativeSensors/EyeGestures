

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
    def __init__(self, clear_up_cb = lambda: None):
        super().__init__()

        self.x = 0
        self.y = 0
        self.clear_up_cb = clear_up_cb

        # Set up the window attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
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
        close_button.clicked.connect(self.clear_up)
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

    def clear_up(self):
        self.clear_up_cb()
        print("cleared up")
        self.close()

class ROI:

    def __init__(self,canvas,root,dimensions_updated_cb = lambda x,y,width,height : None):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.border_radius = 20
        self.rectangle_params = ()
        self.rectangle = None
        self.dimensions_updated_cb = dimensions_updated_cb

        self.canvas = canvas
        self.root = root
        self.resizing = False

    def get_rectangle(self):
        return self.x,self.y,self.width,self.height

    def update_position(self,x,y):
        self.x = x
        self.y = y
        self.dimensions_updated_cb(x,y,self.width,self.height)
        self.update_dimensions(x,y,self.width,self.height)

    def update_dimensions(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if self.rectangle_params != ():
            self.clean_up(self.canvas,*self.rectangle_params)
        self.rectangle_params = self.create_rounded_rectangle(
            self.canvas,
            self.x,
            self.y,
            self.width,
            self.height,
            self.border_radius,
            fill="lightblue")
        self.rectangle = self.rectangle_params[0]
        self.dimensions_updated_cb(x,y,width,height)


    def remove(self):
        print("calling remove")
        if self.rectangle_params != ():
            self.clean_up(self.canvas,*self.rectangle_params)

    def clean_up(self,canvas, *args):
        for item in args:
            canvas.delete(item)

    def create_rounded_rectangle(self,canvas, x, y, width, height, radius, **kwargs):
        """
        Draw a rounded rectangle on Tkinter Canvas.
        Parameters:
        - canvas: Tkinter Canvas object
        - x1, y1: Coordinates of the top left corner
        - x2, y2: Coordinates of the bottom right corner
        - radius: Radius of the rounded corners
        - kwargs: Additional arguments for canvas.create_polygon()
        """
        x1 = x
        y1 = y
        x2 = x + width
        y2 = y + height

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
        arc1 = canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2, start=90, extent=90, style="pieslice", outline="", **kwargs)
        arc2 = canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2, start=0, extent=90, style="pieslice", outline="", **kwargs)
        arc3 = canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2, start=270, extent=90, style="pieslice", outline="", **kwargs)
        arc4 = canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2, start=180, extent=90, style="pieslice", outline="", **kwargs)

        # Create the rectangle
        rectangle = canvas.create_polygon(points, **kwargs, smooth=True)

        canvas.tag_bind(rectangle, "<Enter>", self.on_hover)
        canvas.tag_bind(rectangle, "<Leave>", self.on_leave)
        # canvas.tag_bind(rectangle, "<ButtonPress-1>", self.on_drag_start)
        # canvas.tag_bind("<B1-Motion>", self.on_drag)
        # canvas.tag_bind("<ButtonPress-1>", self.on_drag_start)
        # canvas.tag_bind("<ButtonRelease-1>", self.on_release)
        # canvas.tag_bind("<Motion>", self.on_hover)

        return (rectangle, arc1, arc2, arc3, arc4)

    def on_hover(self,event):
        margin = 50
        if (self.x < event.x and event.x < self.x  + margin) \
            and \
            (self.y < event.y and event.y < self.y  + margin):
            self.root.config(cursor="top_left_corner")
        elif (self.x < event.x and event.x < self.x  + margin) \
            and \
            (self.y + self.height - margin < event.y and event.y < self.y + self.height):
            self.root.config(cursor="bottom_left_corner")
        elif (self.x + self.width - margin < event.x and event.x < self.x + self.width) \
            and \
            (self.y < event.y and event.y < self.y  + margin):
            self.root.config(cursor="top_right_corner")
        elif (self.x + self.width - margin < event.x and event.x < self.x + self.width) \
            and \
            (self.y + self.height - margin < event.y and event.y < self.y + self.height):
            self.root.config(cursor="bottom_right_corner")
        elif self.x < event.x and event.x < self.x  + margin:
            self.root.config(cursor="sb_h_double_arrow")
        elif self.x + self.width - margin < event.x and event.x < self.x + self.width:
            self.root.config(cursor="sb_h_double_arrow")
        elif self.y < event.y and event.y < self.y  + margin:
            self.root.config(cursor="sb_v_double_arrow")
        elif self.y + self.height - margin < event.y and event.y < self.y + self.height:
            self.root.config(cursor="sb_v_double_arrow")
        else:
            self.root.config(cursor="")

        self.canvas.itemconfig(self.rectangle, fill="lightgreen")

    def on_leave(self,event):
        self.canvas.itemconfig(self.rectangle, fill="lightblue")

    def on_release(self,event):
        self.resizing = False

    def on_drag_start(self,event):
        print("start dragging")
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        margin = 50
        if (self.x < event.x and event.x < self.x  + margin) \
            and \
            (self.y < event.y and event.y < self.y  + margin):
            self.resizing = True
        elif (self.x < event.x and event.x < self.x  + margin) \
            and \
            (self.y + self.height - margin < event.y and event.y < self.y + self.height):
            self.resizing = True
        elif (self.x + self.width - margin < event.x and event.x < self.x + self.width) \
            and \
            (self.y < event.y and event.y < self.y  + margin):
            self.resizing = True
        elif (self.x + self.width - margin < event.x and event.x < self.x + self.width) \
            and \
            (self.y + self.height - margin < event.y and event.y < self.y + self.height):
            self.resizing = True
        elif self.x < event.x and event.x < self.x  + margin:
            self.resizing = True
        elif self.x + self.width - margin < event.x and event.x < self.x + self.width:
            self.resizing = True
        elif self.y < event.y and event.y < self.y  + margin:
            self.resizing = True
        elif self.y + self.height - margin < event.y and event.y < self.y + self.height:
            self.resizing = True

    def on_drag(self,event):
        print("dragging")
        margin = 50
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        if not self.resizing:
            self.canvas.move(self.rectangle, dx, dy)
            self.update_position(self.x + dx,self.y + dy)
        else:
            if event.x < self.x + margin:
                self.clean_up(self.canvas,*self.rectangle_params)
                self.x += dx
                self.width -= dx
                self.update_dimensions(
                    self.x,
                    self.y,
                    self.width,
                    self.height)
            elif self.x + self.width - margin < event.x:
                self.clean_up(self.canvas,*self.rectangle_params)
                self.width += dx
                self.update_dimensions(
                    self.x,
                    self.y,
                    self.width,
                    self.height)
            if event.y < self.y + margin:
                self.clean_up(self.canvas,*self.rectangle_params)
                self.y += dy
                self.height -= dy
                self.update_dimensions(
                    self.x,
                    self.y,
                    self.width,
                    self.height)
            elif self.y + self.height - margin < event.y:
                self.clean_up(self.canvas,*self.rectangle_params)
                self.height += dy
                self.update_dimensions(
                    self.x,
                    self.y,
                    self.width,
                    self.height)

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def is_in(self,event):
        return self.x < event.x < self.x + self.width and self.y < event.y < self.y + self.height
    
class RoIMan:

    def __init__(self):
        self.root = None
        self.canvas = None
        self.t = None
        self.roi_counter = 0
        self.rois = []

    def start_painting(self):
        if self.t == None and self.root == None:
            self.t = threading.Thread(target=self.__start_thread)
            self.t.start()

    def __start_thread(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("Rounded Rectangle")
        self.root.attributes("-alpha", 0.5)
        self.root.attributes("-transparentcolor","white")
        self.root.attributes('-topmost',True)
        monitor = get_monitors()[0]
        self.canvas = tk.Canvas(self.root, width=monitor.width-5, height=monitor.height-5, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_hover)

        self.root.mainloop()
        print("painter stopped")

    def on_drag_start(self,event):

        for roi in self.rois:
            if roi.is_in(event):
                roi.on_drag_start(event)
                break

    def on_drag(self,event):
        for roi in self.rois:
            if roi.is_in(event):
                roi.on_drag(event)
                break

    def on_release(self,event):
        for roi in self.rois:
            if roi.is_in(event):
                roi.on_release(event)
                break

    def on_hover(self,event):
        for roi in self.rois:
            if roi.is_in(event):
                roi.on_hover(event)
                break

    def stop_painting(self):
        print("stopping painter")
        self.root.after(1,self.root.destroy)

    def add_roi(self):
        while self.root == None or self.canvas == None:
            pass
        print(self.root,self.canvas)
        self.rois.append(RoIPainter(self.canvas,self.root,self.remove_callback))
        self.roi_counter += 1

    def remove_callback(self):
        self.roi_counter -= 1
        print(self.roi_counter)
        if(self.roi_counter <= 0):
            self.stop_painting()

    def get_all_rois(self):
        return self.rois

class RoIPainter:

    def __init__(self,root,canvas, remove_cb = lambda : None):
        self.remove_cb = remove_cb
        self.roi = ROI(root,canvas,self.position_of_roi_updated)
        self.roi_widget = AceeptRemoveWidget(self.remove)
        self.roi_widget.show()

        self.roi.update_position(50,50)
        self.roi.update_dimensions(200,200,500,500)

    def remove(self):
        self.roi.remove()
        print("roi removed")
        self.remove_cb()
        print("remove cb")

    def position_of_roi_updated(self,x,y,width,height):
        self.roi_widget.move(x,y-100)
        pass

    def on_drag_start(self,event):
        self.roi.on_drag_start(event)

    def on_drag(self,event):
        self.roi.on_drag(event)

    def on_release(self,event):
        self.roi.on_release(event)

    def on_hover(self,event):
        self.roi.on_hover(event)

    def is_in(self,event):
        return self.roi.is_in(event)

def rectangle_class():
    app = QApplication(sys.argv)
    RM = RoIMan()
    RM.start_painting()
    RM.add_roi()
    sys.exit(app.exec_())

if __name__ == '__main__':

    # app = QApplication(sys.argv)
    # accept_remove = AceeptRemoveWidget()
    # accept_remove.show()
    rectangle_class()

    # sys.exit(app.exec_())