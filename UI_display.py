from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QGraphicsOpacityEffect, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QTransform
from PyQt5.QtCore import Qt, QTimer, QEvent, QPropertyAnimation
import sys
import numpy as np
from send_event import QCustomEvent
from os.path import exists
import cv2

class BallDetectionUI(QMainWindow):
    def __init__(self, screen_width, screen_height,main_app):
        super().__init__()

        self.main_app = main_app
        self.setWindowTitle("공 감지 UI")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.state = "WAIT_BALL"

        self.w = screen_width
        self.h = screen_height
        self.speed_value = None
        self.impact_position = None

        print("Initializing UI...")

        self.splash_container = QLabel(self)
        self.splash_container.setGeometry(0, 0, self.w, self.h)
        self.splash_container.setStyleSheet("background-color: white;")
        self.splash_container.setVisible(True)

        splash_pixmap = QPixmap("./resource/splash.png")
        if splash_pixmap.isNull():
            print("Error: Failed to load splash.png, using fallback")
            splash_pixmap = QPixmap(100, 100)
            splash_pixmap.fill(Qt.white)
        splash_width = splash_pixmap.width()
        splash_height = splash_pixmap.height()

        self.splash_image_label = QLabel(self.splash_container)
        self.splash_image_label.setPixmap(splash_pixmap)
        self.splash_image_label.setGeometry(
            (self.w - splash_width) // 2,
            (self.h - splash_height) // 2,
            splash_width,
            splash_height
        )
        self.splash_image_label.setVisible(True)

        self.splash_container.raise_()
        self.update()
        self.repaint()

        self.bg_label = QLabel(self)
        bg_pixmap = QPixmap("./resource/yard.jpg").scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding)
        if bg_pixmap.isNull():
            print("Error: Failed to load yard.jpg")
        self.bg_label.setPixmap(bg_pixmap)
        self.bg_label.setGeometry(0, 0, self.w, self.h)
        self.bg_label.lower()

        self.text_label = QLabel("", self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 140px; color: white; background-color: rgba(0,0,0,120); border-radius: 30px;")
        self.text_label.setGeometry(0, self.h // 4, self.w, 200)

        # ------------ 수정된 배치 시작 ------------
        section_width = int(self.w * 0.3)
        image_height = int(self.h * 0.9)
        margin_top = (self.h - image_height) // 2

        # 속도 텍스트 (좌측)
        self.result_text_label = QLabel(self)
        self.result_text_label.setAlignment(Qt.AlignCenter)
        self.result_text_label.setWordWrap(True)
        self.result_text_label.setStyleSheet("""
            font-size: 50px;
            color: white;
            background-color: rgba(0,0,0,120);
            border-radius: 30px;
            padding: 5px;
        """)
        # self.result_text_label.setContentsMargins(5, 5, 5, 5)


        # self.result_text_label.setGeometry(
        #     50,
        #     self.h - 250 - margin_bottom,
        #     section_width - 50,
        #     300
        # )

        text_width = int(self.w * 0.3)
        text_height = 450

        self.result_text_label.setGeometry(
            (self.w // 2 - text_width) // 2,
            (self.h - text_height) // 2,
            text_width,
            text_height
        )

        # 결과 이미지 (중앙)
        self.result_image_label1 = QLabel(self)
        self.result_image_label1.setGeometry(
            (self.w - section_width) // 2 + 300,
            margin_top,
            section_width + 60,
            image_height + 60
        )
        self.result_image_label1.setAlignment(Qt.AlignCenter)

        self.result_image_label2 = QLabel(self)
        self.result_image_label2.setGeometry(
            (self.w - section_width) // 2 ,
            margin_top+150,
            section_width + 60,
            image_height + 60
        )
        self.result_image_label2.setAlignment(Qt.AlignCenter)

        # 이미지 하나만 할거라 일단 두번째 이미지에 해당하는 코드들 주석 처리
        # # 추출 그래픽 (우측)
        # self.result_image_label2 = QLabel(self)
        # self.result_image_label2.setGeometry(
        #     self.w - section_width - 30 - 100,
        #     margin_top,
        #     section_width,
        #     image_height
        # )
        # self.result_image_label2.setAlignment(Qt.AlignCenter)

        # ------------ 수정된 배치 끝 ------------


        self.next_button = QPushButton("🏑 다시하기", self)
        self.next_button.setStyleSheet("""
            font-size: 40px;
            padding: 10px 20px;
            background-color: #87CEFA;  /* 하늘색 */
            color: white;
            border: 3px solid #1E90FF;  /* 파란색 테두리 */
            border-radius: 10px;
        """)
        self.next_button.setGeometry(
            self.w - 340,  # 화면 우측 상단 위치
            40,            # 상단 여백
            290, 80
        )
        self.next_button.clicked.connect(self.reset_state)
        self,main_app.resume_process()
        self.next_button.setVisible(False)

        self.text_label.setVisible(False)
        self.result_text_label.setVisible(False)
        self.result_image_label1.setVisible(False)
        # self.result_image_label2.setVisible(False)

        QTimer.singleShot(2500, self.show_main_ui)

    def fade_in_widget(self, widget, duration=500):
        widget.setVisible(True)
        opacity = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity)
        animation = QPropertyAnimation(opacity, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        widget._fade_animation = animation

    def fade_out_widget(self, widget, duration=500):
        if not widget.isVisible():
            return
        opacity = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity)
        animation = QPropertyAnimation(opacity, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)

        def on_finished():
            widget.setVisible(False)
            widget.setGraphicsEffect(None)

        animation.finished.connect(on_finished)
        animation.start()
        widget._fade_animation = animation

    def show_main_ui(self):
        print("Showing main UI...")
        self.fade_out_widget(self.splash_container, 800)
        self.text_label.setText("공을 놓으세요")
        self.fade_in_widget(self.text_label, 1000)

    def event(self, event):
        if isinstance(event, QEvent) and hasattr(event, 'callback'):
            event.callback(event.arg)
            return True
        return super().event(event)
    


##
    def show_message(self, message):
        if hasattr(self, 'text_label'):
            self.text_label.setText(message)
            self.fade_in_widget(self.text_label)
        else:
            self.text_label = QLabel(message, self)
            self.text_label.setStyleSheet("color: red; font-size: 48px; font-weight: bold;")
            self.text_label.setGeometry(100, 100, 800, 100)
            self.text_label.show()

    def show_detected_image(self, image_path):
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
            self.fade_in_widget(self.text_label)
            if image_path:
                pixmap = QPixmap(image_path)
                self.result_image_label1.setPixmap(pixmap)
                self.fade_in_widget(self.result_image_label1)
        else:
            self.text_label.setText("공을 놓으세요")
            self.fade_in_widget(self.text_label)
            self.fade_out_widget(self.result_image_label1)
##




    def handle_ir_detected(self, low_frame=None):
        if low_frame is not None:
            if low_frame.shape[2] == 4:
                # OpenCV BGRA → RGBA 변환
                rgba_frame = cv2.cvtColor(low_frame, cv2.COLOR_BGRA2RGBA)
                height, width, channel = rgba_frame.shape
                bytes_per_line = 4 * width
                q_image = QImage(rgba_frame.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
            else:
                # 3채널 처리 (기존대로)
                height, width, channel = low_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(low_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                q_image = q_image.rgbSwapped()

            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(
                self.result_image_label2.width(),
                self.result_image_label2.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.result_image_label2.setPixmap(pixmap)
            self.result_image_label2.setVisible(True)

            if self.state == "WAIT_BALL":
                self.text_label.setText("공을 치세요")
                self.fade_in_widget(self.text_label)
                self.fade_in_widget(self.result_image_label2)
                self.state = "READY_TO_HIT"

            elif self.state == "READY_TO_HIT":
                # 애니메이션 없이 프레임만 즉시 교체
                self.state = "READY_TO_HIT"

                pass  # 위에서 setPixmap만 하면 됨
   

    def handle_camera_detected(self, speed, impact_position, impact_frame=None):
        if self.state == "READY_TO_HIT":
            self.state = "SHOW_RESULT"
            self.fade_out_widget(self.text_label)

            if speed is not None and impact_position is not None:
                x, y = impact_position
                self.result_text_label.setText(f"💨 속도 \n {speed} km/h\n\n⛳ 좌표 \n x : {x}, y : {y}")
            elif speed is not None:
                self.result_text_label.setText(f"💨속도 \n {speed} km/h")
            else:
                self.result_text_label.setText("속도: N/A")

            self.fade_in_widget(self.result_text_label)

            if impact_frame is not None:
                import cv2

                frame_with_marker = impact_frame.copy()
                if impact_position is not None:
                    x, y = impact_position
                    cv2.circle(frame_with_marker, (x, y), 20, (0, 0, 255), 3)

                def to_pixmap(cv_img):
                    height, width, channel = cv_img.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    q_image = q_image.rgbSwapped()
                    pixmap = QPixmap.fromImage(q_image)
                    transform = QTransform().rotate(90)
                    return pixmap.transformed(transform, Qt.SmoothTransformation)

                # pixmap1 = to_pixmap(orig)                # 원본

                pixmap1 = to_pixmap(frame_with_marker) 
                # pixmap2 = to_pixmap(frame_with_marker)   # 마커 있음

                # 크기 조절
                scaled1 = pixmap1.scaled(self.result_image_label1.width(), self.result_image_label1.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # scaled2 = pixmap2.scaled(self.result_image_label2.width(), self.result_image_label2.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                self.result_image_label1.setPixmap(scaled1)
                # self.result_image_label2.setPixmap(scaled2)

                self.fade_in_widget(self.result_image_label1)
                # self.fade_in_widget(self.result_image_label2)

                self.next_button.setVisible(True)
                self.fade_in_widget(self.next_button)

    def reset_state(self):
        self.state = "WAIT_BALL"
        self.text_label.setText("공을 놓으세요")
        self.fade_in_widget(self.text_label)
        self.fade_out_widget(self.result_text_label)
        self.fade_out_widget(self.result_image_label1)
        # self.fade_out_widget(self.result_image_label2)
        self.fade_out_widget(self.next_button)

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
