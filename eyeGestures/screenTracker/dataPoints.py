class Center:
    """Helper representing Center of object with x,y,width,height"""

    def __init__(self, x, y, width, height):
        self.x = (x + width) / 2
        self.y = (y + height) / 2


class Screen:
    """Helper representing screen by making box of width,height"""

    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def getCenter(self):
        """Function returnig center of the screen"""
        return Center(self.x, self.y, self.width, self.height)


class ScreenROI:
    """Helper representing ROI by making box of width,height with x and y offset"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setCenter(self, x, y):
        """Function allowing to move ROI by changing its center"""
        self.x = x - self.width / 2
        self.y = y - self.height / 2

    def getCenter(self):
        """Function returnig center of the ROI"""
        return Center(self.x, self.y, self.width, self.height)

    def getBoundaries(self):
        """Function returnig boundaries of the ROI"""
        return (self.x, self.y, self.width, self.height)


class Display:
    """Helper representing Display by making box of width,height with x and y offset"""

    def __init__(self, width, height, offset_x, offset_y):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y

        # self.buffor = Buffor(20)

    def getCenter(self):
        """Function returnig center of the Display"""
        center_x = (self.offset_x + self.width) / 2
        center_y = (self.offset_y + self.height) / 2
        return (center_x, center_y)
