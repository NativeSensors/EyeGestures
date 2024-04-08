import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide2.QtGui import QPixmap, QPalette, QColor, QPainterPath, QRegion, QMouseEvent
from PySide2.QtCore import Qt, QRectF, QMargins, QPoint
from PySide2.QtGui import QPainter
from PySide2.QtCore import QByteArray
from PySide2.QtSvg import QSvgRenderer
from screeninfo   import get_monitors

class EyeGestureWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.close_events = []

        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        postion_x = int(self.monitor.width/2) + self.monitor.x - 110
        postion_y = 45 + self.monitor.y


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
        self.setGeometry(100, 100, 1000, 700)  # Adjust size as needed
        self.move_to_center()

        self.setWindowTitle("EyeGestures")
        # Buttons
        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.close_event)

        self.label_name = QLabel("EyeGestures")
        # Set text alignment to center
        self.label_name.setAlignment(Qt.AlignCenter)

        info_params_container = QWidget()
        info_params_container_layout = QHBoxLayout()
        info_params_container_layout.setAlignment(Qt.AlignHCenter)
        info_params_container.setLayout(info_params_container_layout)

        self.label_fixation_threshold = QLabel("Fixation: 0.8")
        self.label_fixation_radius  = QLabel("Distance: 500px")

        info_params_container_layout.addWidget(self.label_fixation_threshold)
        info_params_container_layout.addWidget(self.label_fixation_radius)


        progress_bar_container = QWidget()
        progress_bar_container_layout = QHBoxLayout()
        progress_bar_container_layout.setAlignment(Qt.AlignHCenter)
        progress_bar_container.setLayout(progress_bar_container_layout)

        self.fixation_bar = QProgressBar()
        self.fixation_bar.setValue(40)  # Set initial value
        self.fixation_bar.setFixedHeight(100)
        self.fixation_bar.setOrientation(Qt.Orientation.Vertical)
        self.fixation_bar.setTextVisible(False)
        self.fixation_bar.setStyleSheet("""
                                        QProgressBar {
                                            background-color: #06020f;
                                            border-radius: 10px; /* Adjust this value to change the roundness */
                                        }
                                        QProgressBar::chunk {
                                            background-color: #8b125c;
                                            border-radius: 10px; /* Adjust this value to change the roundness */
                                        }
                                        """)

        self.label_fixation  = QLabel("Fixation")
        self.label_fixation_level  = QLabel("40")
        progress_bar_container_layout.addWidget(self.fixation_bar)
        progress_bar_container_layout.addWidget(self.label_fixation)
        progress_bar_container_layout.addWidget(self.label_fixation_level)


        # Set font size
        font = self.label_name.font()
        font.setPointSize(20) # You can adjust the font size as per your requirement
        self.label_name.setFont(font)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # self.image_label.setPixmap(scaled_pixmap)
        main_layout.addWidget(self.label_name)
        main_layout.addWidget(info_params_container)
        main_layout.addWidget(progress_bar_container)
        main_layout.addWidget(self.close_btn)


        self.style_buttons(self.close_btn)

        # this sets windows frameless
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    eyegesture_widget = EyeGestureWidget()
    eyegesture_widget.show()

    sys.exit(app.exec_())
