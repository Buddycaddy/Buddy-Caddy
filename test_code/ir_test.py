# from gpiozero import Button, Device
# from gpiozero.pins.mock import MockFactory
# from multiprocessing import Value
# import time

# # 테스트용 Mock 설정
# # Device.pin_factory = MockFactory()

# # GPIO 핀 번호 설정 (BCM 기준)
# IR1_PIN = 18  # 굴러가는 공 감지
# IR2_PIN = 23  # 공이 놓였는지 확인
# IR3_PIN = 24  # 날아가는 공 감지

# # 거리 설정 (미터 단위)
# DIST_IR2_TO_IR1 = 0.3
# DIST_IR2_TO_IR3 = 0.3

# # 기준 시간 기록용 변수
# ir2_time = Value('d', 0.0)
# lock = ir2_time.get_lock()

# # 속도 계산 함수
# def calculate_speed(t1, t2, distance):
#     if t2 > t1:
#         delta = t2 - t1
#         speed_mps = distance / delta
#         return round(speed_mps * 3.6, 2)  # m/s → km/h 변환
#     return None

# # 각 센서의 콜백 함수
# def on_ir2_triggered():
#     with lock:
#         ir2_time.value = time.time()
#         print(f"[IR2] 공 놓임 감지됨 - 시간 기록: {ir2_time.value:.6f}")

# def on_ir1_triggered():
#     with lock:
#         if ir2_time.value > 0:
#             t1 = time.time()
#             speed = calculate_speed(ir2_time.value, t1, DIST_IR2_TO_IR1)
#             print(f"[IR1] 굴러가는 공 감지됨 - 속도: {speed} km/h")
#             ir2_time.value = 0

# def on_ir3_triggered():
#     with lock:
#         if ir2_time.value > 0:
#             t3 = time.time()
#             speed = calculate_speed(ir2_time.value, t3, DIST_IR2_TO_IR3)
#             print(f"[IR3] 날아가는 공 감지됨 - 속도: {speed} km/h")
#             ir2_time.value = 0

# # 센서 객체 생성 및 콜백 연결
# ir1 = Button(IR1_PIN, pull_up=True, bounce_time=0.001)
# ir2 = Button(IR2_PIN, pull_up=True, bounce_time=0.001)
# ir3 = Button(IR3_PIN, pull_up=True, bounce_time=0.001)

# ir1.when_pressed = on_ir1_triggered
# ir2.when_pressed = on_ir2_triggered
# ir3.when_pressed = on_ir3_triggered

# # 루프 시작
# print("IR 센서 3개 속도 측정 시작 (Ctrl+C로 종료)")
# try:
#     while True:
#         time.sleep(0.01)
# except KeyboardInterrupt:
    # print("\n종료됨.")









# import RPi.GPIO as GPIO
# import time

# # GPIO 핀 번호 설정 (BCM 모드 기준)
# IR1_PIN = 18
# IR2_PIN = 23
# IR3_PIN = 24

# # GPIO 초기 설정
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(IR1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(IR2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(IR3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# try:
#     print("3개 IR 센서 상태 동시 출력 시작 (Ctrl+C로 종료)")
#     while True:
#         ir1 = "감지됨" if GPIO.input(IR1_PIN) == 0 else "없음"
#         ir2 = "감지됨" if GPIO.input(IR2_PIN) == 0 else "없음"
#         ir3 = "감지됨" if GPIO.input(IR3_PIN) == 0 else "없음"

#         print(f"[IR1]: {ir1}  |  [IR2]: {ir2}  |  [IR3]: {ir3}")
#         time.sleep(0.2)

# except KeyboardInterrupt:
#     print("\n프로그램 종료")

# finally:
#     GPIO.cleanup()

import RPi.GPIO as GPIO
import time

# IR 센서 핀 설정
# IR_PINS = [18, 23, 24]  
#5 맨앞
#6,13 중간 상단,하단  
#18,23,24 맨뒤  위/ 중간 /아래

IR_PINS = [5, 6, 13,18,23,24]# 후측 하단(18), 전측 하단(23), 후측 상단(24)

def ir_callback(pin):
    """IR 센서가 트리거될 때 호출되는 콜백 함수"""
    print(f"IR sensor on pin {pin} triggered at {time.time()}")

def setup_ir_sensors():
    """IR 센서 초기화"""
    GPIO.setmode(GPIO.BCM)  # BCM 모드 사용
    GPIO.setwarnings(False)
    
    for pin in IR_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 풀업 저항 사용
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=ir_callback, bouncetime=200)  # 이벤트 감지 설정
        print(f"IR sensor on pin {pin} initialized")

def main():
    try:
        setup_ir_sensors()
        print("IR sensor test started. Press Ctrl+C to exit.")
        while True:
            time.sleep(0.1)  # CPU 사용량 줄이기
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()  # GPIO 리소스 정리

if __name__ == "__main__":
    main()




