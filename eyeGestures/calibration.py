
import time


class Calibrator:
    """Class representing a calibration process"""

    def __init__(self, width, height, _time=60):
        self.width = width
        self.height = height
        self.time = _time

        self.run = False
        self.t_start = 0

        self.on_finish = None
        self.points = []

    def start(self, on_finish):
        """Function starting calibration."""
        self.t_start = time.time()
        self.run = True

        self.on_finish = on_finish

    def get_training_point(self):
        """Returns training point for calibration."""

        if not self.run:
            return self.points[0]

        else:
            time_step = self.time/len(self.points)
            index = int((time.time() - self.t_start)/time_step) * \
                ((time.time() - self.t_start) > 0)

            if (index < 0 or index >= len(self.points)):
                self.run = False

                if not self.on_finish is None:
                    self.on_finish()
                    return self.points[0]

            return self.points[index]

    def inProgress(self):
        return self.run
