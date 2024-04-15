

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

class AceeptRemoveWidget(QWidget):
    def __init__(self, clear_up_cb = lambda: None, accept_cb = lambda: None):
        super().__init__()

        self.x = 0
        self.y = 0
        self.accept_cb = accept_cb
        self.clear_up_cb = clear_up_cb
        # Set up the window attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        layout = QHBoxLayout(self)
        layout.setSpacing(0)

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
        accept_button.clicked.connect(self.accept)
        layout.addWidget(accept_button)

        # Create Close button with close icon
        close_button = QPushButton(QtGui.QIcon.fromTheme("dialog-close"), "❌")
        close_button.clicked.connect(self.clear_up_cb)
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

    def accept(self):
        self.accept_cb()
        self.hide()

    def show_again(self):
        self.show()

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

    def show(self):
        self.update_dimensions(self.x,self.y,self.width,self.height)

    def remove(self):
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

class RoIPainter:

    def __init__(self,id,root,canvas, off_x = 0, off_y = 0, remove_cb = lambda : None, position_update_cb = lambda : None, hide_cb = lambda: None):
        self.id = id
        self.remove_cb = remove_cb
        self.position_update_cb = position_update_cb
        self.hidden = False

        self.roi = ROI(root,canvas,self.position_of_roi_updated)
        self.roi_widget = AceeptRemoveWidget(self.remove, self.hide)
        self.roi_widget.show()

        self.roi.update_position(50,50)
        self.roi.update_dimensions(200+off_x,200+off_y,500,500)

    def remove(self):
        self.roi_widget.close()
        self.roi.remove()
        self.remove_cb(self.id)

    def hide(self):
        self.roi.remove()
        self.hidden = True
        pass

    def show(self):
        self.hidden = False
        self.roi.show()
        self.roi_widget.show_again()

    def position_of_roi_updated(self,x,y,width,height):
        self.roi_widget.move(x,y-100)
        self.position_update_cb(self.id,(x,y,width,height))
        pass

    def get_rectangle(self):
        return (
            self.roi.x,
            self.roi.y,
            self.roi.width,
            self.roi.height
        )

    def on_drag_start(self,event):
        self.roi.on_drag_start(event)

    def on_drag(self,event):
        self.roi.on_drag(event)

    def on_release(self,event):
        self.roi.on_release(event)

    def on_hover(self,event):
        self.roi.on_hover(event)

    def is_in(self,event):
        return self.roi.is_in(event) and not self.hidden
class RoIMan:

    def __init__(self):
        self.root = None
        self.canvas = None
        self.t = None
        self.roi_counter = 0
        self.rois = dict()
        self.dragged_roi = None

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

    def on_drag_start(self,event):

        for key in self.rois:
            if self.rois[key].is_in(event):
                self.dragged_roi = self.rois[key]
                self.rois[key].on_drag_start(event)
                break

    def on_drag(self,event):
        if self.dragged_roi.is_in(event):
            self.dragged_roi.on_drag(event)


    def on_release(self,event):
        for key in self.rois:
            if self.rois[key].is_in(event):
                self.rois[key].on_release(event)
                break

    def on_hover(self,event):
        for key in self.rois:
            if self.rois[key].is_in(event):
                self.rois[key].on_hover(event)
                break

    def stop_painting(self):
        if self.t != None and self.root != None:
            self.root.after(1,self.root.destroy)
            self.t = None
            self.root = None

    def add_roi(self, remove_cb = lambda id : None, position_update_cb = lambda id, rect_params : None):
        self.start_painting()

        def remove_callback(id):
            remove_cb(id)
            self.rois.pop(id)
            self.roi_counter = len(self.rois)

        while self.root == None or self.canvas == None:
            pass
        id = len(self.rois)
        self.rois[id] = RoIPainter(
            id, # id
            self.canvas,
            self.root,
            self.roi_counter*5,
            self.roi_counter*5,
            remove_callback,
            position_update_cb)

        self.roi_counter = len(self.rois)
        return id

    # def remove_callback(self,id):
    #     self.rois.pop(id)
    #     self.roi_counter = len(self.rois)

    def remove(self):
        while len(self.rois) > 0:
            self.rois[list(self.rois.keys())[0]].remove()

        self.stop_painting()

    def get_all_rois(self):
        return self.rois

    def show(self):
        for key in self.rois:
            print(f"showing: {self.rois[key]}")
            self.rois[key].show()

    def close_event(self):
        if self.t != None and self.root != None:
            self.stop_painting()

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