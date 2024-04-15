import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QSlider, QLineEdit, QSpacerItem, QSizePolicy
from PySide2.QtGui import QPixmap, QPalette, QColor, QPainterPath, QRegion, QMouseEvent
from PySide2.QtCore import Qt, QRectF, QMargins, QPoint
from PySide2.QtGui import QPainter, QFont
from PySide2.QtCore import QByteArray
from PySide2.QtSvg import QSvgRenderer
from screeninfo   import get_monitors

from appUtils.ActivationZone import RoIMan
from appUtils.RoiViewer import RoiViewer

import hashlib
import os

class InputFileNameWidget(QWidget):

    def __init__(self,text_updated_cb) -> None:
        super().__init__()
        random_hash = hashlib.sha256(os.urandom(16)).hexdigest()[:8]
        self.text_updated_cb = text_updated_cb
        self.is_editable = True

        layout = QVBoxLayout()
        self.label = QLabel("💾 File:")
        self.text_input = QLineEdit(f"collection_{random_hash}")
        self.text_input.setReadOnly(not self.is_editable)  # Set initial read-only state
        self.text_input.textChanged.connect(self.on_text_updated)
        self.unsetReadOnly()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)

        self.setLayout(layout)

    def setReadOnly(self):
        self.is_editable = False
        self.text_input.setReadOnly(not self.is_editable)  # Set initial read-only state
        self.text_input.setStyleSheet("""
                                QLineEdit {
                                    background-color: #14171A;
                                    border: 1px solid #14171A;
                                    color: #F5F8FA;
                                    border-radius: 5px; /* Adjust this value to change the roundness */
                                    font-family: Poppins;
                                    padding: 5px;
                                }
                                """)

    def unsetReadOnly(self):
        self.is_editable = True
        self.text_input.setReadOnly(not self.is_editable)  # Set initial read-only state
        self.text_input.setStyleSheet("""
                                QLineEdit {
                                    background-color: #14171A;
                                    border: 1px solid #657786;
                                    color: #F5F8FA;
                                    border-radius: 5px; /* Adjust this value to change the roundness */
                                    font-family: Poppins;
                                    padding: 5px;
                                }
                                """)

    def on_text_updated(self, updated_text):
        # Execute the callback function with the new text
        if self.text_updated_cb:
            self.text_updated_cb(updated_text)

    def getText(self):
        return self.text_input.text()

class AdvancedSettings(QWidget):

    def __init__(self,
                 update_fixation_cb,
                 update_radius_label,
                 cursor_visible,
                 cursor_not_visible,
                 screen_recording_enable,
                 screen_recording_disabled,
                 _toggle_callback) -> None:
        super().__init__()

        layout = QVBoxLayout()

        self.update_fixation_cb = update_fixation_cb
        self.update_radius_label = update_radius_label
        self.cursor_visible = cursor_visible
        self.cursor_not_visible = cursor_not_visible
        self.screen_recording_enable = screen_recording_enable
        self.screen_recording_disabled = screen_recording_disabled
        self._toggle_callback = _toggle_callback

        self.control_btn = QPushButton('🞂 ⚙️Advanced settings')
        self.control_btn.setCheckable(True)  # Make the button a toggle button
        self.control_btn.clicked.connect(self.__toggle)

        self.control_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                margin: 0px;
                height: 40px;
                width: 200px;
                border-radius: 5px;
                color: #E1E8ED;
                border: none;
                text-align: left;
                background-color: #14171A;
                font-family: Poppins;
            }
            QPushButton:hover {
                background-color: #818992;
            }
            QPushButton:pressed {
                background-color: #212426;
            }
            """)


        self.slider_fixation = QSlider(Qt.Horizontal)
        self.slider_fixation.setMinimum(0)
        self.slider_fixation.setMaximum(10)
        self.slider_fixation.setValue(8)
        self.slider_fixation.valueChanged.connect(self.update_fixation_label)

        self.slider_radius = QSlider(Qt.Horizontal)
        self.slider_radius.setMinimum(1)
        self.slider_radius.setMaximum(500)
        self.slider_radius.setValue(400)
        self.slider_radius.valueChanged.connect(self.update_radius_label)

        self.cursor_toggle_btn = QPushButton("Cursor Visible")
        self.cursor_toggle_btn.setCheckable(True)  # Make the button a toggle button
        self.cursor_toggle_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 5px;
                    background-color: #14171A;
                    color: #eff0f1;
                    margin: 5px;
                    padding: 10px;
                    padding: 10px 20px;  /* Increase padding for bigger size */
                    font-family: Poppins;
                }
                QPushButton:hover {
                    background-color: #818992;
                }
                QPushButton:pressed {
                    background-color: #212426;
                }
            """)
        self.cursor_toggle_btn.clicked.connect(self.toggle_visible_cursor)

        self.screen_recording_tgl_btn = QPushButton("Screen recording ON 🔴")
        self.screen_recording_tgl_btn.setCheckable(True)  # Make the button a toggle button
        self.screen_recording_tgl_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 5px;
                    background-color: #14171A;
                    color: #eff0f1;
                    margin: 5px;
                    padding: 10px;
                    padding: 10px 20px;  /* Increase padding for bigger size */
                    font-family: Poppins;
                }
                QPushButton:hover {
                    background-color: #818992;
                }
                QPushButton:pressed {
                    background-color: #212426;
                }
            """)
        self.screen_recording_tgl_btn.clicked.connect(self.toggle_recording_screen)

        self.slider_radius = QSlider(Qt.Horizontal)
        self.slider_radius.setMinimum(1)
        self.slider_radius.setMaximum(500)
        self.slider_radius.setValue(400)
        self.slider_radius.valueChanged.connect(self.update_radius_label)


        self.label_fixation_threshold = QLabel("Fixation: 0.8")
        self.label_radius_threshold   = QLabel("Radius: 500px")

        self.fixation_layout = QHBoxLayout()
        self.fixation_layout.addWidget(self.label_fixation_threshold)
        self.fixation_layout.addWidget(self.slider_fixation)

        self.radius_layout = QHBoxLayout()
        self.radius_layout.addWidget(self.label_radius_threshold)
        self.radius_layout.addWidget(self.slider_radius)

        self.cursor_toggle_layout = QHBoxLayout()
        self.cursor_toggle_layout.addWidget(self.cursor_toggle_btn)

        self.screen_recording_layout = QHBoxLayout()
        self.screen_recording_layout.addWidget(self.screen_recording_tgl_btn)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.control_btn,  alignment=Qt.AlignLeft)

        layout.addLayout(button_layout)
        layout.addLayout(self.fixation_layout)
        layout.addLayout(self.radius_layout)
        layout.addLayout(self.cursor_toggle_layout)
        layout.addLayout(self.screen_recording_layout)
        spacer = QSpacerItem(0, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        self.setLayout(layout)
        self.hide()

    def hide(self):
        self.label_fixation_threshold.hide()
        self.slider_fixation.hide()
        self.label_radius_threshold.hide()
        self.slider_radius.hide()
        self.screen_recording_tgl_btn.hide()
        self.cursor_toggle_btn.hide()
        self.control_btn.setText('🞂  ⚙️Advanced settings')
        self.setFixedHeight(100)

    def show_again(self):
        self.label_fixation_threshold.show()
        self.slider_fixation.show()
        self.label_radius_threshold.show()
        self.slider_radius.show()
        self.screen_recording_tgl_btn.show()
        self.cursor_toggle_btn.show()
        self.control_btn.setText('🞃 ⚙️Advanced settings')
        self.setFixedHeight(300)

    def update_fixation_label(self, value):
        # Convert integer value to float (0.0 to 1.0)
        self.label_fixation_threshold.setText(f"Fixation: {value/10}")
        self.update_fixation_cb(value/10)

    def update_radius_label(self, value):
        # Convert integer value to float (0.0 to 1.0)
        self.label_radius_threshold.setText(f"Radius: {value}px")
        self.update_radius_cb(value)

    def toggle_visible_cursor(self):
        text = "Cursor not visible ⚫" if self.cursor_toggle_btn.isChecked() else "Cursor visible 🟠"
        self.cursor_toggle_btn.setText(text)

        if text == "Cursor visible 🟠":
            self.cursor_visible()
        else:
            self.cursor_not_visible()

    def toggle_recording_screen(self):
        text = "Screen recording OFF ⚫" if self.screen_recording_tgl_btn.isChecked() else "Screen recording ON 🔴"
        self.screen_recording_tgl_btn.setText(text)

        if text == "Screen recording ON 🔴":
            self.screen_recording_enable()
        else:
            self.screen_recording_disabled()

    def __toggle(self):
        self.show_again() if self.control_btn.isChecked() else self.hide()
        self._toggle_callback()

class StartStopWidget(QWidget):

    def __init__(self,stop_cb,start_cb) -> None:
        super().__init__()

        self.stop_cb = stop_cb
        self.start_cb = start_cb

        progress_bar_container_layout = QHBoxLayout()
        progress_bar_container_layout.setAlignment(Qt.AlignHCenter)

        self.start_stop_btn = QPushButton("🟢 Start")
        self.start_stop_btn.setCheckable(True)  # Make the button a toggle button
        self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 5px;
                    background-color: #14171A;
                    color: #eff0f1;
                    margin: 5px;
                    padding: 10px;
                    padding: 10px 20px;  /* Increase padding for bigger size */
                    font-family: Poppins;
                }
                QPushButton:hover {
                    background-color: #818992;
                }
                QPushButton:pressed {
                    background-color: #212426;
                }
            """)
        self.start_stop_btn.clicked.connect(self.toggle_start_stop)

        self.fixation_bar = QProgressBar()
        self.fixation_bar.setValue(0)  # Set initial value
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

        self.label_fixation        = QLabel("Fixation")
        self.label_fixation_level  = QLabel("0.0")

        progress_bar_container_layout.addWidget(self.start_stop_btn)
        spacer = QSpacerItem(90, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        progress_bar_container_layout.addSpacerItem(spacer)
        progress_bar_container_layout.addWidget(self.fixation_bar)
        progress_bar_container_layout.addWidget(self.label_fixation)
        progress_bar_container_layout.addWidget(self.label_fixation_level)

        self.setLayout(progress_bar_container_layout)

    def update_fixation(self,value):
        self.label_fixation_level.setText(f"{value:.2f}")
        self.fixation_bar.setValue(int(value * 100))

    def toggle_start_stop(self):
        text = "🔴 Stop" if self.start_stop_btn.isChecked() else "🟢 Start"
        self.start_stop_btn.setText(text)

        if text == "🟢 Start":
            self.stop_cb()
        else:
            self.start_cb()

        # Perform actions based on button state here (optional)

class EyeGestureWidget(QWidget):
    def __init__(self,
                start_cb = lambda : None,
                stop_cb = lambda : None,
                update_fixation_cb = lambda value : None,
                update_radius_cb = lambda value : None,
                text_updated_cb = lambda text : None,
                cursor_visible = lambda : None,
                cursor_not_visible = lambda : None,
                screen_recording_enable = lambda : None,
                screen_recording_disabled = lambda : None):
        super().__init__()

        self.start_cb = start_cb
        self.stop_cb  = stop_cb

        self.close_events = []
        self.roiMan = RoIMan()
        self.roiViewer = RoiViewer()

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
        self.setGeometry(100, 100, 1050, 750)  # Adjust size as needed
        self.move_to_center()

        self.setWindowTitle("EyeGestures")
        # Buttons
        self.close_btn = QPushButton('😢 Close')
        self.close_btn.clicked.connect(self.close_event)

        self.add_roi_btn = QPushButton('➕ Add')
        self.add_roi_btn.clicked.connect(self.add_roi)

        self.show_roi_btn = QPushButton('🔍 Show')
        self.show_roi_btn.clicked.connect(self.show_roi)

        self.label_name = QLabel("EyeGestures")
        # Set text alignment to center
        self.label_name.setAlignment(Qt.AlignCenter)

        # Set font size
        font = self.label_name.font()
        font.setPointSize(20) # You can adjust the font size as per your requirement
        self.label_name.setFont(font)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(self.label_name)

        self.startStop = StartStopWidget(self.__stop_cb,self.__start_cb)
        main_layout.addWidget(self.startStop)

        self.text_input = InputFileNameWidget(text_updated_cb)
        main_layout.addWidget(self.text_input)

        self.adv_settings = AdvancedSettings(
            update_fixation_cb,
            update_radius_cb,
            cursor_visible,
            cursor_not_visible,
            screen_recording_enable,
            screen_recording_disabled,
            self._toggle_callback)
        main_layout.addWidget(self.adv_settings)

        main_layout.addWidget(self.roiViewer)

        roi_buttons_layout = QHBoxLayout()
        roi_buttons_layout.setSpacing(0)

        roi_buttons_layout.addWidget(self.show_roi_btn,2)
        roi_buttons_layout.addWidget(self.add_roi_btn,1)
        main_layout.addLayout(roi_buttons_layout)

        # Add a spacer at the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        main_layout.addWidget(self.close_btn)


        # Set font bold for button2
        self.add_roi_btn.setStyleSheet(
            """
            QPushButton {
                padding: 0px; margin: 0px;
                border: 2px solid #657786;
                height: 40px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                color: #E1E8ED;
                border-right: none;
                border-top: none;
                border-bottom: none;
                background-color: #14171A;
                font-family: Poppins;
            }
            QPushButton:hover {
                background-color: #818992;
            }
            QPushButton:pressed {
                background-color: #212426;
            }
            """)

        self.show_roi_btn.setStyleSheet(
            """
            QPushButton {
                padding: 0px; margin: 0px;
                border: 2px solid #657786;
                height: 40px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                color: #eff0f1;
                border-right: none;
                border-left: none;
                border-top: none;
                border-bottom: none;
                background-color: #14171A;
                font-family: Poppins;
            }
            QPushButton:hover {
                background-color: #818992;
            }
            QPushButton:pressed {
                background-color: #212426;
            }
            """)

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

    def _toggle_callback(self):
        if self.height() == 750:
            self.setFixedHeight(1000)
        else:
            self.setFixedHeight(750)

        # this sets windows frameless
        self.resize(400,self.frameGeometry().height())
        radius = 10.0
        path = QPainterPath()
        # self.resize(440,220)
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)


    def __stop_cb(self):
        self.text_input.unsetReadOnly()
        self.stop_cb()

    def __start_cb(self):
        self.text_input.setReadOnly()
        self.start_cb()

    def get_text(self):
        return self.text_input.getText()

    def update_fixation(self,value):
        self.startStop.update_fixation(value)

    def add_close_event(self,clsoe_callback):
        self.close_events.append(clsoe_callback)

    def close_event(self):

        for event in self.close_events:
            event()

        self.roiMan.remove()
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
                    background-color: #14171A;
                    color: #eff0f1;
                    margin: 5px;
                    padding: 10px;
                    padding: 10px 20px;  /* Increase padding for bigger size */
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

    def rm_roi(self,id):
        self.roiViewer.rm_rectangle(id)
        self.roiViewer.update()

    def update_roi(self,id,rect_params):
        # TODO: maybe those parameters could be handled better?
        rois = self.roiMan.get_all_rois()
        for key in rois:
            self.roiViewer.add_rectangle(
                key,
                rois[key].get_rectangle(),
                self.monitor.width,
                self.monitor.height
            )
        self.roiViewer.update()

    def add_roi(self):
        rois = self.roiMan.get_all_rois()
        if len(rois) < 10:
            self.roiMan.add_roi(self.rm_roi,self.update_roi)
            for key in rois:
                self.roiViewer.add_rectangle(
                    key,
                    rois[key].get_rectangle(),
                    self.monitor.width,
                    self.monitor.height)
            self.roiViewer.update()

    def get_rois_w_detection(self,x,y):
        rois = self.roiMan.get_all_rois()
        ret_data = []
        for key in rois:
            r_x, r_y, r_w, r_h = rois[key].get_rectangle()
            if  r_x < x < r_x + r_w and r_y < y < r_y + r_h:
                self.roiViewer.update_rectangle_color(
                    key,"#c03dff70"
                )
                ret_data.append((1, [r_x, r_y, r_w, r_h]))
            else:
                self.roiViewer.update_rectangle_color(
                    key,"#c03dff"
                )
                ret_data.append((0, [r_x, r_y, r_w, r_h]))
        return ret_data

    def update_dot_viewer(self,x,y):
        # TODO: maybe those parameters could be handled better?
        self.roiViewer.add_dot(
            0,
            (x,y,0,0),
            self.monitor.width,
            self.monitor.height
        )
        self.roiViewer.update()

    def show_roi(self):
        self.roiMan.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set default font and size
    font = QFont("Arial", 20)  # You can change "Arial" to your preferred font
    app.setFont(font)

    eyegesture_widget = EyeGestureWidget()
    eyegesture_widget.show()

    sys.exit(app.exec_())
