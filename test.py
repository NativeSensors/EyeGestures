import sys
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt, QTimer, QRect
from PySide2.QtGui import QTransform

class WarningPill(QWidget):
    def __init__(self, parent, position, text, rotate=False):
        super(WarningPill, self).__init__(parent)
        self.setGeometry(position[0], position[1], 100, 40)
        self.setStyleSheet("background-color: yellow; border-radius: 10px;")

        # Add a label for displaying text
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 100, 40)

class OverlayWidget(QWidget):
    def __init__(self):
        super(OverlayWidget, self).__init__()

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Layout for the overlay widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("This is your main screen overlay"))

        # Create warning pills on each edge and add them to the layout
        self.warning_pills = [
            WarningPill(self, (0, 0), "Top Left", rotate=True),
            WarningPill(self, (self.width() - 100, 0), "Top Right"),
            WarningPill(self, (0, self.height() - 40), "Bottom Left"),
            WarningPill(self, (self.width() - 100, self.height() - 40), "Bottom Right", rotate=True)
        ]

        for pill in self.warning_pills:
            layout.addWidget(pill)

        # Setup a timer to update the widget's size and positions
        timer = QTimer(self)
        timer.timeout.connect(self.updateGeometry)
        timer.start(100)

    def paintEvent(self, event):
        # Set a semi-transparent background color
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 100)))
        painter.drawRect(self.rect())

    def updateGeometry(self):
        # Update the widget's size and positions of warning pills
        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_rect)

        for i, pill in enumerate(self.warning_pills):
            if i == 0:
                pill.setGeometry(0, 0, 100, 40)
            elif i == 1:
                pill.setGeometry(self.width() - 100, 0, 100, 40)
            elif i == 2:
                pill.setGeometry(0, self.height() - 40, 100, 40)
            elif i == 3:
                pill.setGeometry(self.width() - 100, self.height() - 40, 100, 40)

def main():
    app = QApplication(sys.argv)
    overlay = OverlayWidget()
    overlay.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
