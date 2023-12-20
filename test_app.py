import sys

from PySide2.QtWidgets import QApplication
from appUtils.EyeGestureWidget import EyeGestureWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = EyeGestureWidget()
    widget.show()
    widget.set_calibrate_btn(widget.set_calibrate)
    widget.set_disable_btn(widget.set_disconnected)
    sys.exit(app.exec_())
