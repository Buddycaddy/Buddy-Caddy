# try:
#     import RPi.GPIO as GPIO
# except ImportError:
#     print("RPi.GPIO not found, using emulator")
from gpiozero import Button, Device
from gpiozero.pins.mock import MockFactory
import time
import json

# Pin Factory를 MockFactory로 설정
Device.pin_factory = MockFactory()

IR_PIN = 17

def ir_callback():
    timestamp = time.time()
    print(json.dumps({"event": "ir_trigger", "timestamp": timestamp}))

def setup_ir_sensor():
    ir_sensor = Button(IR_PIN, pull_up=True)  # GPIO 핀을 풀업 설정
    ir_sensor.when_pressed = ir_callback  # 버튼이 눌렸을 때 콜백 실행
    return ir_sensor

if __name__ == "__main__":
    try:
        ir_sensor = setup_ir_sensor()
        print("IR sensor ready")
        while True:
            time.sleep(1)  # 메인 루프에서 대기
    except KeyboardInterrupt:
        print("Exiting program")

# def ir_callback(channel):
#     timestamp = time.time()
#     print(json.dumps({"event": "ir_trigger", "timestamp": timestamp}))

# def setup_ir_sensor():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(IR_PIN, GPIO.FALLING, callback=ir_callback, bouncetime=200)

# if __name__ == "__main__":
#     try:
#         setup_ir_sensor()
#         print("IR sensor ready")
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         GPIO.cleanup()