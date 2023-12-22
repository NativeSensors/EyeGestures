import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import pyautogui
import threading

class WindowsCursor():

    def __init__(self,radius,thickness):
        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 200
        self.thickness = thickness
        self.radius = radius
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

    def __update_window_position(self, root):
        root.geometry(f"+{self.x}+{self.y}")
        root.after(10, lambda: self.__update_window_position(root))  # Schedule the next update

        self.image = self.__create_transparent_rectangle_with_semi_transparent_circle((self.root.winfo_width(), self.root.winfo_height()))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.label.configure(image=self.tk_image)


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
        self.root.attributes("-transparentcolor", "black")

        # Schedule the update of the window position
        self.root.after(10, lambda: self.__update_window_position(self.root))

        self.root.mainloop()

    def close_event(self):
        def destroy_root():
            self.root.destroy()

        # Schedule the destruction of the Tkinter window in the main thread
        self.root.after(0, destroy_root)

    def move(self,x,y):
        self.x = x - self.width//2
        self.y = y - self.height//2

    def set_radius(self, radius):
        if self.root != None:
            radius = max(radius,1)
            radius = min(radius,200)

            self.circle_radius1 = radius
            self.circle_radius2 = radius - 1