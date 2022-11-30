import os
import sys
import threading
from decimal import Decimal, ROUND_HALF_UP

from PySide6 import QtCore, QtGui, QtWidgets

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./libs/")))
from libs import loggle
from libs.loggle import logger
from libs.tobiiresearch.implementation import EyeTracker


class GazeManager:
    def __init__(self):
        self.my_eyetracker = EyeTracker.find_all_eyetrackers()[0]
        self.gaze_thr = threading.Thread(
            target=self.my_eyetracker.subscribe_to(
                EyeTracker.EYETRACKER_GAZE_DATA, self.gaze_callback, as_dictionary=True
            ),
            daemon=True,
        )
        self.gaze_thr.start()

    def gaze_callback(self, gaze_data):
        global global_gaze_data
        left_gaze_point = gaze_data["left_gaze_point_on_display_area"]
        right_gaze_point = gaze_data["right_gaze_point_on_display_area"]
        global_gaze_data = (
            float(
                Decimal(str((left_gaze_point[0] + right_gaze_point[0]) / 2)).quantize(
                    Decimal("0.0001"), rounding=ROUND_HALF_UP
                )
            ),
            float(
                Decimal(str((left_gaze_point[1] + right_gaze_point[1]) / 2)).quantize(
                    Decimal("0.0001"), rounding=ROUND_HALF_UP
                )
            ),
        )


class MainWin(QtWidgets.QMainWindow):
    def __init__(self, center: QtWidgets.QWidget):
        super().__init__()
        self.setCentralWidget(center)
        self.resize(self.screen().size() * 0.8)


class CentralWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.first_win_width = self.width()
        self.first_win_height = self.height()

        self.gaze_data_label = QtWidgets.QLabel("data", self)
        self.gaze_data_label.setGeometry(10, 10, 200, 20)

        self.pointer_ratio = 0.05
        self.pointer_size = self.size().width() * self.pointer_ratio
        self.pointer_label = QtWidgets.QLabel(self)
        self.cursor_style = f"""
        QLabel{{
            background-color: rgba(83,191,245,100);
            min-width: %spx;
            min-height: %spx;
            max-width: %spx;
            max-height: %spx;
            border-radius: %spx;
        }}
        """ % (
            self.pointer_size,
            self.pointer_size,
            self.pointer_size,
            self.pointer_size,
            self.pointer_size / 2,
        )
        self.pointer_label.setStyleSheet(self.cursor_style)
        self.pointer_label.move(50, 50)

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.__refresh)
        self.refresh_timer.start(1)

    def __refresh(self):
        global global_gaze_data

        screen_geo = self.screen().geometry().size()

        gaze_pos = (
            global_gaze_data[0] * screen_geo.width(),
            global_gaze_data[1] * screen_geo.height(),
        )

        print(win.pos(), gaze_pos)

        # self.gaze_data_label.setText(
        #     "gaze data: (%s, %s)" % (gaze_qpoint_local.x(), gaze_qpoint_local.y())
        # )

        #     self.pointer_label.move(
        #         self.width() * global_gaze_data[0] - self.pointer_label.width() / 2,
        #         self.height() * global_gaze_data[1] - self.pointer_label.height() / 2,
        #     )


if __name__ == "__main__":
    loggle.set_file_handler(logger, "./logs/tobii_log.log", "INFO")

    global_gaze_data = None
    gaze = GazeManager()

    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()

    panel = CentralWidget()
    win = MainWin(center=panel)

    win.show()
    app.exec_()
