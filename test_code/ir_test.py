


# # import RPi.GPIO as GPIO
# # import time

# # # GPIO 핀 번호 설정 (BCM 모드 기준)
# # IR1_PIN = 18
# # IR2_PIN = 23
# # IR3_PIN = 24

# # # GPIO 초기 설정
# # GPIO.setmode(GPIO.BCM)
# # GPIO.setup(IR1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# # GPIO.setup(IR2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# # GPIO.setup(IR3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# # try:
# #     print("3개 IR 센서 상태 동시 출력 시작 (Ctrl+C로 종료)")
# #     while True:
# #         ir1 = "감지됨" if GPIO.input(IR1_PIN) == 0 else "없음"
# #         ir2 = "감지됨" if GPIO.input(IR2_PIN) == 0 else "없음"
# #         ir3 = "감지됨" if GPIO.input(IR3_PIN) == 0 else "없음"

# #         print(f"[IR1]: {ir1}  |  [IR2]: {ir2}  |  [IR3]: {ir3}")
# #         time.sleep(0.2)

# # except KeyboardInterrupt:
# #     print("\n프로그램 종료")

# # finally:
# #     GPIO.cleanup()

# import RPi.GPIO as GPIO
# import time

# # IR 센서 핀 설정
# IR_PINS = [18, 23, 24]  # 후측 하단(18), 전측 하단(23), 후측 상단(24)

# def ir_callback(pin):
#     """IR 센서가 트리거될 때 호출되는 콜백 함수"""
#     print(f"IR sensor on pin {pin} triggered at {time.time()}")

# def setup_ir_sensors():
#     """IR 센서 초기화"""
#     GPIO.setmode(GPIO.BCM)  # BCM 모드 사용
#     GPIO.setwarnings(False)
    
#     for pin in IR_PINS:
#         GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 풀업 저항 사용
#         GPIO.add_event_detect(pin, GPIO.FALLING, callback=ir_callback, bouncetime=200)  # 이벤트 감지 설정
#         print(f"IR sensor on pin {pin} initialized")

# def main():
#     try:
#         setup_ir_sensors()
#         print("IR sensor test started. Press Ctrl+C to exit.")
#         while True:
#             time.sleep(0.1)  # CPU 사용량 줄이기
#     except KeyboardInterrupt:
#         print("Exiting program")
#     finally:
#         GPIO.cleanup()  # GPIO 리소스 정리

# if __name__ == "__main__":
#     main()






import RPi.GPIO as GPIO
import time

IR_PINS = [18, 23, 24]  # 후측 하단(18), 전측 하단(23), 후측 상단(24)

def setup_ir_sensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in IR_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"IR sensor on pin {pin} initialized")

def main():
    try:
        setup_ir_sensors()
        print("IR 센서 빛 감지(막혀있지 않을 때) 출력 시작 (Ctrl+C로 종료)")
        prev_state = [None] * len(IR_PINS)
        while True:
            for idx, pin in enumerate(IR_PINS):
                state = GPIO.input(pin)
                if state == 1 and prev_state[idx] != 1:
                    print(f"IR sensor on pin {pin} 빛 감지됨 at {time.time()}")
                prev_state[idx] = state
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()