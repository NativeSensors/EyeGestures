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

    def set_svg_data(self, svg_data):
        self.svg_renderer.load(QByteArray(svg_data.encode()))
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        self.svg_renderer.render(painter)

class EyeGestureWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.close_events = []

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
        self.setGeometry(100, 100, 1000, 100)  # Adjust size as needed
        self.move_to_center()

        # Buttons
        self.calibrate_btn = QPushButton('Calibrate')
        self.disable_btn = QPushButton('Disable')
        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.close_event)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        # Image
        self.image_label = QLabel(self)

        red = "#ac5453"
        self.color = red
        svg_data =  f"""
            <svg width="15" height="15" viewBox="0 0 15 15" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="iris-gradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <!-- Gradient stops for the iris -->
                </radialGradient>
            </defs>
            <circle cx="7.5" cy="7.5" r="6" fill="#c5c5c5" /> <!-- Sclera -->
            <circle cx="7.5" cy="7.5" r="5.2" fill="#141415" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="4.8" fill="{self.color}" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="3.5" fill="#c5c5c5" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="3" fill="#141415" /> <!-- Pupil -->
            <circle cx="10" cy="6" r="1.5" fill="#c5c5c5" /> <!-- Light -->
            </svg>
            """
        
        self.svgWidget = SvgWidget(svg_data)
        print(f"self.svgWidget: {self.svgWidget}")
        # self.image_label.setPixmap(scaled_pixmap)

        main_layout.addWidget(self.svgWidget)
        main_layout.addWidget(self.calibrate_btn)
        main_layout.addWidget(self.disable_btn)
        main_layout.addWidget(self.close_btn)

        self.style_buttons(self.calibrate_btn
                           ,self.disable_btn
                           ,self.close_btn
                           )

        self.adjustSize()
        self.resize(400,self.frameGeometry().height())
        radius = 10.0
        path = QPainterPath()
        # self.resize(440,220)
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.setLayout(main_layout)
        self.move(postion_x, postion_y)

    def add_close_event(self,clsoe_callback):
        self.close_events.append(clsoe_callback)

    def close_event(self):
    
        for event in self.close_events:
            event()

        self.close() 

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

    def updateEye(self):
        svg_data =  f"""
            <svg width="15" height="15" viewBox="0 0 15 15" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="iris-gradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <!-- Gradient stops for the iris -->
                </radialGradient>
            </defs>
            <circle cx="7.5" cy="7.5" r="6" fill="#c5c5c5" /> <!-- Sclera -->
            <circle cx="7.5" cy="7.5" r="5.2" fill="#141415" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="4.8" fill="{self.color}" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="3.5" fill="#c5c5c5" /> <!-- Iris -->
            <circle cx="7.5" cy="7.5" r="3" fill="#141415" /> <!-- Pupil -->
            <circle cx="10" cy="6" r="1.5" fill="#c5c5c5" /> <!-- Light -->
            </svg>
            """
        self.svgWidget.set_svg_data(svg_data)

    def set_calibrate_btn(self,callback):
        self.calibrate_btn.clicked.connect(callback)

    def set_disable_btn(self,callback):
        self.disable_btn.clicked.connect(callback)

    def set_calibrate(self):
        yellow = "#e6b505"
        self.color = yellow
        self.updateEye()
        
    def set_ready(self):
        green = "#0e6711"
        self.color = green
        self.updateEye()
        
    def set_disconnected(self):
        red = "#ac5453"
        self.color = red
        self.updateEye()