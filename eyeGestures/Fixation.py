"""Module providing a fixation detection."""


class Fixation:
    """Class performing Fixation"""

    def __init__(self, x, y, radius=100):
        self.radius = radius
        self.fixation = 0.0
        self.x = x
        self.y = y
        pass

    def process(self, x, y):
        """Function processing x and y estimated points for fixation detection"""

        if (x - self.x)**2 + (y - self.y)**2 < self.radius**2:
            self.fixation = min(self.fixation + 0.02, 1.0)
        else:
            self.x = x
            self.y = y
            self.fixation = 0

        return self.fixation
