import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PySide2.QtGui import QPixmap, QPalette, QColor, QPainterPath, QRegion, QMouseEvent
from PySide2.QtCore import Qt, QRectF, QMargins, QPoint
from PySide2.QtGui import QPainter
from PySide2.QtCore import QByteArray
from PySide2.QtSvg import QSvgRenderer
from screeninfo   import get_monitors

class SvgWidget(QWidget):
    def __init__(self, svg_data, parent=None):
        super(SvgWidget, self).__init__(parent)
        self.svg_renderer = QSvgRenderer(QByteArray(svg_data.encode()))

    def paintEvent(self, event):
        painter = QPainter(self)
        self.svg_renderer.render(painter)

class EyeGestureWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        postion_x = int(self.monitor.width/2) + self.monitor.x - 110
        postion_y = 45 + self.monitor.y

        # Set window flags to remove title bar and make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(1, 4, 4))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

        # Window positioning
        self.setGeometry(100, 100, 400, 200)  # Adjust size as needed
        self.move_to_center()

        # Buttons
        self.button1 = QPushButton('Calibrate')
        self.button2 = QPushButton('Disable')
        # self.button3 = QPushButton('Button 3')

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        # Image
        self.image_label = QLabel(self)
        pixmap = QPixmap('eye.png')  # Replace with your image path
        scaled_pixmap = pixmap.scaled(30,30, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        green = "#0e6711"
        red = "#ac5453"
        yellow = "#e6b505"

        svg_data =  f"""
            <svg width="15" height="15" viewBox="0 0 15 15" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="iris-gradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <!-- Gradient stops for the iris -->
                </radialGradient>
            </defs>
            <circle cx="7.5" cy="7.5" r="6" fill="#c5c5c5" /> <!-- Sclera -->
            <circle cx="7.5" cy="7.5" r="5" fill="{yellow}" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="3" fill="#141415" /> <!-- Pupil -->
            <circle cx="10" cy="6" r="1.5" fill="#c5c5c5" /> <!-- Light -->
            </svg>
            """
        self.svgWidget = SvgWidget(svg_data)

        # self.image_label.setPixmap(scaled_pixmap)

        main_layout.addWidget(self.svgWidget)
        main_layout.addWidget(self.button1)
        main_layout.addWidget(self.button2)
        # main_layout.addWidget(self.button3)

        self.style_buttons(self.button1
                           ,self.button2
                        #    ,self.button3
                           )

        self.adjustSize()
        self.resize(300,self.frameGeometry().height())
        radius = 10.0
        path = QPainterPath()
        # self.resize(440,220)
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.setLayout(main_layout)
        self.move(postion_x, postion_y)

    def move_to_center(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 4  # Adjust to bring the window to the top middle
        self.move(int(x), int(y))

    def style_buttons(self, *buttons):
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 5px;
                    background-color: #DD555b62;
                    color: #eff0f1;
                    margin: 5px;
                    padding: 10px;
                    padding: 10px 20px;  /* Increase padding for bigger size */
                    font-size: 14px;  /* Larger font size */
                    font-family: Poppins;
                }
                QPushButton:hover {
                    background-color: #818992;
                }
                QPushButton:pressed {
                    background-color: #212426;
                }
            """)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.oldPos:
            return

        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.oldPos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = EyeGestureWidget()
    widget.show()
    sys.exit(app.exec_())
