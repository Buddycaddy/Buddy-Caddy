from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import sys

class BallDetectionUI(QWidget):
    def __init__(self, screen_width, screen_height):
        super().__init__()

        self.setWindowTitle("공 감지 UI")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.state = "WAIT_BALL"

        self.w = screen_width
        self.h = screen_height
        self.speed_value = 28

        # 배경 이미지
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("yard.jpg").scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding))
        self.bg_label.setGeometry(0, 0, self.w, self.h)

        # splash 흰 배경
        self.splash_label = QLabel(self)
        self.splash_label.setStyleSheet("background-color: white;")
        self.splash_label.setGeometry(0, 0, self.w, self.h)
        self.splash_label.setVisible(True)

        # splash 이미지
        self.splash_image_label = QLabel(self)
        splash_pixmap = QPixmap("splash.png")
        splash_width = splash_pixmap.width()
        splash_height = splash_pixmap.height()
        self.splash_image_label.setPixmap(splash_pixmap)
        self.splash_image_label.setGeometry(
            (self.w - splash_width) // 2,
            (self.h - splash_height) // 2,
            splash_width,
            splash_height
        )
        self.splash_image_label.setVisible(True)

        # 안내 텍스트
        self.text_label = QLabel("", self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 52px; color: white; background-color: rgba(0,0,0,120);")
        self.text_label.setGeometry(0, self.h // 4, self.w, 100)

        # 결과 텍스트
        text_area_width = int(self.w * 0.2)
        margin_left = 20
        text_box_height = int(self.h * 0.22)
        self.result_text_label = QLabel(self)
        self.result_text_label.setAlignment(Qt.AlignCenter)
        self.result_text_label.setWordWrap(True)
        self.result_text_label.setStyleSheet("font-size: 34px; color: white; background-color: rgba(0,0,0,120);")
        self.result_text_label.setContentsMargins(5, 5, 5, 5)
        self.result_text_label.setGeometry(margin_left, (self.h - text_box_height) // 2, text_area_width, text_box_height)

        # 결과 이미지 2개
        image_width = int(self.w * 2 / 5)
        image_height = int(self.h * 0.75)
        gap_shift = 40
        image_gap_reduction = 20

        self.result_image_label1 = QLabel(self)
        self.result_image_label1.setGeometry(text_area_width + gap_shift, (self.h - image_height) // 2, image_width, image_height)
        self.result_image_label1.setAlignment(Qt.AlignCenter)

        self.result_image_label2 = QLabel(self)
        self.result_image_label2.setGeometry(text_area_width + image_width + gap_shift - image_gap_reduction, (self.h - image_height) // 2, image_width, image_height)
        self.result_image_label2.setAlignment(Qt.AlignCenter)

        # 버튼 (테스트용 - 센서 대체)
        self.ir_button = QPushButton("IR센서: 공 감지됨", self)
        self.ir_button.setGeometry((self.w - 400) // 2, self.h - 250, 400, 60)
        self.ir_button.setStyleSheet("font-size: 24px; background-color: #ffffffcc;")
        self.ir_button.clicked.connect(self.handle_ir_detected)

        self.camera_button = QPushButton("카메라: 네트 맞음", self)
        self.camera_button.setGeometry((self.w - 400) // 2, self.h - 160, 400, 60)
        self.camera_button.setStyleSheet("font-size: 24px; background-color: #ffffffcc;")
        self.camera_button.clicked.connect(self.handle_camera_detected)

        # 초기 UI 상태 설정
        self.text_label.setVisible(False)
        self.result_text_label.setVisible(False)
        self.result_image_label1.setVisible(False)
        self.result_image_label2.setVisible(False)
        self.ir_button.setVisible(False)
        self.camera_button.setVisible(False)

        QTimer.singleShot(1000, self.show_main_ui)

    def show_main_ui(self):
        self.splash_label.setVisible(False)
        self.splash_image_label.setVisible(False)
        self.text_label.setText("공을 놓으세요")
        self.text_label.setVisible(True)
        self.ir_button.setVisible(True)
        self.camera_button.setVisible(True)

    def handle_ir_detected(self):
        if self.state == "WAIT_BALL":
            self.text_label.setText("공을 치세요")
            self.state = "READY_TO_HIT"

    def handle_camera_detected(self):
        if self.state == "READY_TO_HIT":
            self.state = "SHOW_RESULT"
            self.text_label.setVisible(False)

            self.result_text_label.setText(f"\U0001F3C3속도: {self.speed_value} km/h")
            self.result_text_label.setVisible(True)

            img1 = QPixmap("result1.png").scaled(self.result_image_label1.width(), self.result_image_label1.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img2 = QPixmap("result1.png").scaled(self.result_image_label2.width(), self.result_image_label2.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.result_image_label1.setPixmap(img1)
            self.result_image_label2.setPixmap(img2)
            self.result_image_label1.setVisible(True)
            self.result_image_label2.setVisible(True)

            QTimer.singleShot(2000, self.reset_state)

    def reset_state(self):
        self.state = "WAIT_BALL"
        self.text_label.setVisible(True)
        self.text_label.setText("공을 놓으세요")
        self.result_text_label.setVisible(False)
        self.result_image_label1.setVisible(False)
        self.result_image_label2.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screens = app.screens()
    target_screen = screens[1] if len(screens) > 1 else screens[0]
    geometry = target_screen.geometry()
    width, height = geometry.width(), geometry.height()
    window = BallDetectionUI(width, height)
    window.move(geometry.x(), geometry.y())
    window.showFullScreen()
    sys.exit(app.exec_())





# # import tkinter as tk
# # import json

# # class GolfUI:
# #     def __init__(self, root):
# #         self.root = root
# #         self.root.title("Golf Simulator")
# #         self.label = tk.Label(root, text="Waiting for ball...", font=("Arial", 24))
# #         self.label.pack(pady=20)
# #         self.speed_label = tk.Label(root, text="Speed: N/A", font=("Arial", 18))
# #         self.speed_label.pack(pady=10)
# #         self.impact_label = tk.Label(root, text="Impact: N/A", font=("Arial", 18))
# #         self.impact_label.pack(pady=10)

# #     def update(self, data):
# #         if "detected" in data and data["detected"]:
# #             self.label.config(text="Hit the ball!")
# #         if "speed" in data and data["speed"]:
# #             self.speed_label.config(text=f"Speed: {data['speed']:.2f} m/s")
# #         if "impact_position" in data and data["impact_position"]:
# #             x, y = data["impact_position"]
# #             self.impact_label.config(text=f"Impact: ({x}, {y})")

# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = GolfUI(root)
# #     test_data = {"detected": True, "speed": 20.5, "impact_position": (100, 200)}
# #     app.update(test_data)
# #     root.mainloop()

# #     #test