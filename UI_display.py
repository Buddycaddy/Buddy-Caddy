from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import sys
import numpy as np
from send_event import QCustomEvent


class BallDetectionUI(QMainWindow):
    def __init__(self, screen_width, screen_height):
        super().__init__()

        self.setWindowTitle("공 감지 UI")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.state = "WAIT_BALL"

        self.w = screen_width
        self.h = screen_height
        self.speed_value = None
        self.impact_position = None

        # 배경 이미지
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("./resource/yard.jpg").scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding))
        self.bg_label.setGeometry(0, 0, self.w, self.h)

        # splash 흰 배경
        self.splash_label = QLabel(self)
        self.splash_label.setStyleSheet("background-color: white;")
        self.splash_label.setGeometry(0, 0, self.w, self.h)
        self.splash_label.setVisible(True)

        # splash 이미지
        self.splash_image_label = QLabel(self)
        splash_pixmap = QPixmap("./resource/splash.png")
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
        self.text_label.setStyleSheet("font-size: 120px; color: white; background-color: rgba(0,0,0,120);")
        self.text_label.setGeometry(0, self.h // 4, self.w, 160)

        # 결과 텍스트
        text_area_width = int(self.w * 0.2)
        margin_left = 20
        text_box_height = int(self.h * 0.22)
        self.result_text_label = QLabel(self)
        self.result_text_label.setAlignment(Qt.AlignCenter)
        self.result_text_label.setWordWrap(True)
        self.result_text_label.setStyleSheet("font-size: 40px; color: white; background-color: rgba(0,0,0,120);")
        self.result_text_label.setContentsMargins(5, 5, 5, 5)
        self.result_text_label.setGeometry(margin_left-15, (self.h - text_box_height) // 2, text_area_width+30, text_box_height)

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

        # 초기 UI 상태 설정
        self.text_label.setVisible(False)
        self.result_text_label.setVisible(False)
        self.result_image_label1.setVisible(False)
        self.result_image_label2.setVisible(False)

        QTimer.singleShot(1000, self.show_main_ui)

    def customEvent(self, event):

        if isinstance(event, QCustomEvent):
            event.execute()

    def show_main_ui(self):
        self.splash_label.setVisible(False)
        self.splash_image_label.setVisible(False)
        self.text_label.setText("공을 놓으세요")
        self.text_label.setVisible(True)

    def show_message(self, message):
        if hasattr(self, 'text_label'):
            self.text_label.setText(message)
        else:
            self.text_label = QLabel(message, self)
            self.text_label.setStyleSheet("color: red; font-size: 48px; font-weight: bold;")
            self.text_label.setGeometry(100, 100, 800, 100)
            self.text_label.show()

    def show_detected_image(self, image_path):
        from os.path import exists

        if not exists(image_path):
            print(f"[경고] 이미지 경로가 잘못되었습니다: {image_path}")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"[경고] 이미지를 불러올 수 없습니다: {image_path}")
            return

        pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if hasattr(self, 'result_label'):
            self.result_label.setPixmap(pixmap)
            self.result_label.setVisible(True)
            self.result_label.raise_()
        else:
            self.result_label = QLabel(self)
            self.result_label.setPixmap(pixmap)
            self.result_label.setGeometry(
                (self.w - pixmap.width()) // 2,
                (self.h - pixmap.height()) // 2 + 150,
                pixmap.width(),
                pixmap.height()
            )
            self.result_label.setStyleSheet("background-color: white; border: 2px solid black;")
            self.result_label.setAlignment(Qt.AlignCenter)
            self.result_label.setVisible(True)
            self.result_label.raise_()

    def show_ball_detected(self, detected, image_path=None):
        if detected:
            self.text_label.setText("공을 치세요")
            if image_path:
                pixmap = QPixmap(image_path)
                self.result_image_label1.setPixmap(pixmap)
                self.result_image_label1.setVisible(True)
        else:
            self.text_label.setText("공을 놓으세요")
            self.result_image_label1.setVisible(False)

    def handle_ir_detected(self):
        print(self.state)
        if self.state == "WAIT_BALL":
            self.text_label.setText("공을 치세요")
            self.state = "READY_TO_HIT"

    def handle_camera_detected(self, speed, impact_position, impact_frame=None):
        if self.state == "READY_TO_HIT":
            self.state = "SHOW_RESULT"
            self.text_label.setVisible(False)

            if speed is not None:
                self.result_text_label.setText(f"\U0001F3C3속도: {speed} km/h\n위치: {impact_position if impact_position else 'N/A'}")
            else:
                self.result_text_label.setText("속도: N/A\n위치: N/A")
            self.result_text_label.setVisible(True)

            # 임팩트 프레임 표시
            if impact_frame is not None:
                height, width, channel = impact_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(impact_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                q_image = q_image.rgbSwapped()  # BGR to RGB
                pixmap = QPixmap.fromImage(q_image)
                pixmap = pixmap.scaled(self.result_image_label1.width(), self.result_image_label1.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.result_image_label1.setPixmap(pixmap)
                self.result_image_label1.setVisible(True)

            img2 = QPixmap("result1.png").scaled(self.result_image_label2.width(), self.result_image_label2.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.result_image_label2.setPixmap(img2)
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




# 화면 이쁘게 할랬는데 제대로 안되서 일단 주석처리함
# from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
# from PyQt5.QtGui import QPixmap, QImage
# from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QEvent
# import sys
# import numpy as np
# from send_event import QCustomEvent
# import logging

# logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")

# class BallDetectionUI(QMainWindow):
#     def __init__(self, screen_width, screen_height):
#         super().__init__()

#         self.setWindowTitle("공 감지 UI")
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         self.setGeometry(0, 0, screen_width, screen_height)
#         self.state = "WAIT_BALL"

#         self.w = screen_width
#         self.h = screen_height
#         self.speed_value = None
#         self.impact_position = None

#         # 배경 이미지
#         self.bg_label = QLabel(self)
#         self.bg_label.setPixmap(QPixmap("./resource/yard.jpg").scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding))
#         self.bg_label.setGeometry(0, 0, self.w, self.h)

#         # splash 흰 배경
#         self.splash_label = QLabel(self)
#         self.splash_label.setStyleSheet("background-color: white;")
#         self.splash_label.setGeometry(0, 0, self.w, self.h)
#         self.splash_label.setVisible(True)
#         self.splash_label.setWindowOpacity(1.0)  # 초기 투명도 설정

#         # splash 이미지
#         self.splash_image_label = QLabel(self)
#         splash_pixmap = QPixmap("./resource/splash.png")
#         splash_width = splash_pixmap.width()
#         splash_height = splash_pixmap.height()
#         self.splash_image_label.setPixmap(splash_pixmap)
#         self.splash_image_label.setGeometry(
#             (self.w - splash_width) // 2,
#             (self.h - splash_height) // 2,
#             splash_width,
#             splash_height
#         )
#         self.splash_image_label.setVisible(True)

#         # 안내 텍스트
#         self.text_label = QLabel("", self)
#         self.text_label.setAlignment(Qt.AlignCenter)
#         self.text_label.setStyleSheet("""
#             font-size: 120px; 
#             color: white; 
#             background-color: rgba(0, 0, 0, 150); 
#             border-radius: 20px;
#             padding: 20px;
#         """)
#         self.text_label.setGeometry(0, self.h // 4, self.w, 160)
#         self.text_label.setWindowOpacity(0.0)  # 초기 투명도 설정

#         # 결과 텍스트
#         text_area_width = int(self.w * 0.2)
#         margin_left = 20
#         text_box_height = int(self.h * 0.22)
#         self.result_text_label = QLabel(self)
#         self.result_text_label.setAlignment(Qt.AlignCenter)
#         self.result_text_label.setWordWrap(True)
#         self.result_text_label.setStyleSheet("""
#             font-size: 40px; 
#             color: white; 
#             background-color: rgba(0, 0, 0, 150); 
#             border-radius: 15px;
#             padding: 10px;
#         """)
#         self.result_text_label.setContentsMargins(5, 5, 5, 5)
#         self.result_text_label.setGeometry(margin_left - 15, (self.h - text_box_height) // 2, text_area_width + 30, text_box_height)
#         self.result_text_label.setWindowOpacity(0.0)  # 초기 투명도 설정

#         # 결과 이미지 2개
#         image_width = int(self.w * 2 / 5)
#         image_height = int(self.h * 0.75)
#         gap_shift = 40
#         image_gap_reduction = 20

#         self.result_image_label1 = QLabel(self)
#         self.result_image_label1.setGeometry(text_area_width + gap_shift, (self.h - image_height) // 2, image_width, image_height)
#         self.result_image_label1.setAlignment(Qt.AlignCenter)
#         self.result_image_label1.setStyleSheet("background-color: rgba(255, 255, 255, 50); border: 2px solid white; border-radius: 10px;")
#         self.result_image_label1.setWindowOpacity(0.0)

#         self.result_image_label2 = QLabel(self)
#         self.result_image_label2.setGeometry(text_area_width + image_width + gap_shift - image_gap_reduction, (self.h - image_height) // 2, image_width, image_height)
#         self.result_image_label2.setAlignment(Qt.AlignCenter)
#         self.result_image_label2.setStyleSheet("background-color: rgba(255, 255, 255, 50); border: 2px solid white; border-radius: 10px;")
#         self.result_image_label2.setWindowOpacity(0.0)

#         # 초기 UI 상태 설정
#         self.text_label.setVisible(False)
#         self.result_text_label.setVisible(False)
#         self.result_image_label1.setVisible(False)
#         self.result_image_label2.setVisible(False)

#         # 스플래시 화면 페이드아웃 애니메이션
#         QTimer.singleShot(1000, self.show_main_ui)

#     def customEvent(self, event):
#         logging.debug(f"Received event: {type(event)}")
#         if isinstance(event, QCustomEvent):
#             event.execute()
#         else:
#             logging.warning(f"Unknown event type: {type(event)}")

#     def show_main_ui(self):
#         # 스플래시 화면 페이드아웃
#         self.fade_out_widget(self.splash_label, 1000)
#         self.fade_out_widget(self.splash_image_label, 1000)
        
#         # 메인 텍스트 페이드인
#         self.text_label.setVisible(True)
#         self.text_label.setText("공을 놓으세요")
#         self.fade_in_widget(self.text_label, 1000)

#     def fade_in_widget(self, widget, duration):
#         """위젯을 페이드인 애니메이션으로 표시"""
#         widget.setVisible(True)
#         animation = QPropertyAnimation(widget, b"windowOpacity")
#         animation.setDuration(duration)
#         animation.setStartValue(0.0)
#         animation.setEndValue(1.0)
#         animation.setEasingCurve(QEasingCurve.InOutQuad)
#         animation.start()

#     def fade_out_widget(self, widget, duration):
#         """위젯을 페이드아웃 애니메이션으로 숨김"""
#         animation = QPropertyAnimation(widget, b"windowOpacity")
#         animation.setDuration(duration)
#         animation.setStartValue(widget.windowOpacity())
#         animation.setEndValue(0.0)
#         animation.setEasingCurve(QEasingCurve.InOutQuad)
#         animation.finished.connect(lambda: widget.setVisible(False))
#         animation.start()

#     def slide_in_widget(self, widget, duration, start_pos, end_pos):
#         """위젯을 슬라이드인 애니메이션으로 표시"""
#         widget.setVisible(True)
#         animation = QPropertyAnimation(widget, b"pos")
#         animation.setDuration(duration)
#         animation.setStartValue(start_pos)
#         animation.setEndValue(end_pos)
#         animation.setEasingCurve(QEasingCurve.InOutQuad)
#         animation.start()

#     def show_message(self, message):
#         if hasattr(self, 'text_label'):
#             self.text_label.setText(message)
#             self.fade_in_widget(self.text_label, 500)
#         else:
#             self.text_label = QLabel(message, self)
#             self.text_label.setStyleSheet("color: red; font-size: 48px; font-weight: bold; background-color: rgba(0, 0, 0, 150); border-radius: 10px;")
#             self.text_label.setGeometry(100, 100, 800, 100)
#             self.text_label.setVisible(True)
#             self.fade_in_widget(self.text_label, 500)

#     def show_detected_image(self, image_path):
#         from os.path import exists

#         if not exists(image_path):
#             logging.warning(f"[경고] 이미지 경로가 잘못되었습니다: {image_path}")
#             return

#         pixmap = QPixmap(image_path)
#         if pixmap.isNull():
#             logging.warning(f"[경고] 이미지를 불러올 수 없습니다: {image_path}")
#             return

#         pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

#         if hasattr(self, 'result_label'):
#             self.result_label.setPixmap(pixmap)
#             self.fade_in_widget(self.result_label, 500)
#             self.result_label.raise_()
#         else:
#             self.result_label = QLabel(self)
#             self.result_label.setPixmap(pixmap)
#             self.result_label.setGeometry(
#                 (self.w - pixmap.width()) // 2,
#                 (self.h - pixmap.height()) // 2 + 150,
#                 pixmap.width(),
#                 pixmap.height()
#             )
#             self.result_label.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px;")
#             self.result_label.setAlignment(Qt.AlignCenter)
#             self.fade_in_widget(self.result_label, 500)
#             self.result_label.raise_()

#     def show_ball_detected(self, detected, image_path=None):
#         if detected:
#             self.text_label.setText("공을 치세요")
#             self.fade_in_widget(self.text_label, 500)
#             if image_path:
#                 pixmap = QPixmap(image_path)
#                 self.result_image_label1.setPixmap(pixmap)
#                 self.fade_in_widget(self.result_image_label1, 500)
#         else:
#             self.text_label.setText("공을 놓으세요")
#             self.fade_in_widget(self.text_label, 500)
#             self.fade_out_widget(self.result_image_label1, 500)

#     def handle_ir_detected(self):
#         logging.debug(f"Current state: {self.state}")
#         print(f"Current state: {self.state}")
#         if self.state == "WAIT_BALL":
#             self.text_label.setText("공을 치세요")
#             self.fade_in_widget(self.text_label, 500)
#             self.state = "READY_TO_HIT"

#     def handle_camera_detected(self, speed, impact_position, impact_frame=None):
#         if self.state == "READY_TO_HIT":
#             self.state = "SHOW_RESULT"
#             self.fade_out_widget(self.text_label, 500)

#             if speed is not None:
#                 self.result_text_label.setText(f"\U0001F3C3 속도: {speed} km/h\n위치: {impact_position if impact_position else 'N/A'}")
#             else:
#                 self.result_text_label.setText("속도: N/A\n위치: N/A")
#             self.fade_in_widget(self.result_text_label, 500)

#             # 임팩트 프레임 표시
#             if impact_frame is not None:
#                 height, width, channel = impact_frame.shape
#                 bytes_per_line = 3 * width
#                 q_image = QImage(impact_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
#                 q_image = q_image.rgbSwapped()  # BGR to RGB
#                 pixmap = QPixmap.fromImage(q_image)
#                 pixmap = pixmap.scaled(self.result_image_label1.width(), self.result_image_label1.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
#                 self.result_image_label1.setPixmap(pixmap)
#                 self.slide_in_widget(self.result_image_label1, 500, 
#                                     (self.result_image_label1.x(), self.h), 
#                                     (self.result_image_label1.x(), (self.h - self.result_image_label1.height()) // 2))

#             img2 = QPixmap("result1.png").scaled(self.result_image_label2.width(), self.result_image_label2.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
#             self.result_image_label2.setPixmap(img2)
#             self.slide_in_widget(self.result_image_label2, 500, 
#                                 (self.result_image_label2.x(), -self.result_image_label2.height()), 
#                                 (self.result_image_label2.x(), (self.h - self.result_image_label2.height()) // 2))

#             QTimer.singleShot(2000, self.reset_state)

#     def reset_state(self):
#         self.state = "WAIT_BALL"
#         self.text_label.setText("공을 놓으세요")
#         self.fade_in_widget(self.text_label, 500)
#         self.fade_out_widget(self.result_text_label, 500)
#         self.fade_out_widget(self.result_image_label1, 500)
#         self.fade_out_widget(self.result_image_label2, 500)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     screens = app.screens()
#     target_screen = screens[1] if len(screens) > 1 else screens[0]
#     geometry = target_screen.geometry()
#     width, height = geometry.width(), geometry.height()
#     window = BallDetectionUI(width, height)
#     window.move(geometry.x(), geometry.y())
#     window.showFullScreen()
#     sys.exit(app.exec_())