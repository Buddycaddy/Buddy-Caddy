from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEvent  # 상단 import 필수
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

    def show_main_ui(self):
        self.splash_label.setVisible(False)
        self.splash_image_label.setVisible(False)
        self.text_label.setText("공을 놓으세요")
        self.text_label.setVisible(True)


    # 추가
    def event(self, event):  # 이벤트 핸들러 메서드 추가
        if isinstance(event, QEvent) and hasattr(event, 'callback'):
            event.callback()
            return True
        return super().event(event)
    # 추가


    # 추가
    # BallDetectionUI 클래스 내부에 아래 두 메서드 추가
    def show_message(self, message):
        if hasattr(self, 'text_label'):
            self.text_label.setText(message)
        else:
            self.text_label = QLabel(message, self)
            self.text_label.setStyleSheet("color: red; font-size: 48px; font-weight: bold;")
            self.text_label.setGeometry(100, 100, 800, 100)
            self.text_label.show()

    # def show_detected_image(self, image_path):
    #     if hasattr(self, 'result_label'):
    #         self.result_label.setPixmap(QPixmap(image_path).scaled(640, 480, Qt.KeepAspectRatio))
    #     else:
    #         self.result_label = QLabel(self)
    #         self.result_label.setGeometry(300, 200, 640, 480)
    #         self.result_label.setPixmap(QPixmap(image_path).scaled(640, 480, Qt.KeepAspectRatio))
    #         self.result_label.show()

    
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
    # 추가




    def handle_ir_detected(self):
        if self.state == "WAIT_BALL":
            self.text_label.setText("공을 치세요")
            self.state = "READY_TO_HIT"

    def handle_camera_detected(self, speed, impact_position):
        if self.state == "READY_TO_HIT":
            self.state = "SHOW_RESULT"
            self.text_label.setVisible(False)

            if speed is not None:
                self.result_text_label.setText(f"\U0001F3C3속도: {speed} km/h\n위치: {impact_position if impact_position else 'N/A'}")
            else:
                self.result_text_label.setText("속도: N/A\n위치: N/A")
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

