import sys
import random
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QKeyEvent
from PySide2.QtCore import Qt, QTimer, QEvent
import keyboard

from pynput import keyboard

class RedDotWidget(QWidget):
    
    def __init__(self, diameter=50):
        super(RedDotWidget,self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.setFocusPolicy(Qt.StrongFocus)  # Allow the widget to receive focus
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_randomly)
        self.timer.start(1000)  # Update position every 1000 milliseconds (1 second)

        # Start listening for the 'q' key press in the background
        self.listener = keyboard.Listener(on_press=self.on_quit)
        self.listener.start()


    def move_randomly(self):
        # Get the size of the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = random.randint(0, screen_geometry.width() - self.diameter)
        y = random.randint(0, screen_geometry.height() - self.diameter)
        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.diameter, self.diameter)

    def keyPressEvent(self, event):
        print(f"event key: {event.key()}")
        if event.key() == Qt.Key_Q:  # Close the widget if the 'q' key is pressed
            self.close()

    def on_quit(self,key):
        print(key)
        # Stop listening to the keyboard input and close the application
        self.close()
        self.listener.join()

    def closeEvent(self, event):
        # Ensure the application quits completely
        QApplication.quit()


    def showEvent(self, event):
        self.setFocus()  # Set focus to the widget when it is shown

if __name__ == '__main__':
    app = QApplication(sys.argv)
    red_dot_widget = RedDotWidget(diameter=50)
    red_dot_widget.show()
    sys.exit(app.exec_())
