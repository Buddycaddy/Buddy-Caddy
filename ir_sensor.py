# try:
#     import RPi.GPIO as GPIO
# except ImportError:
#     print("RPi.GPIO not found, using emulator")
from gpiozero import Button, Device
from gpiozero.pins.mock import MockFactory
from multiprocessing import Queue, Value
import time

# Pin Factory를 MockFactory로 설정 (PC 테스트용)
Device.pin_factory = MockFactory()

IR_PIN = 17  # IR 센서가 연결된 GPIO 핀 번호

def ir_disconnected_callback(queue):
    print("IR sensor 전송")
    queue.put({"source": "ir_sensor", "event": "ir_trigger", "timestamp": time.time()})


# 프로세스 동작 테스트용 코드
def setup_ir_sensor(ir_queue, is_ready):
    ir_sensor = Button(IR_PIN, pull_up=True)
    has_triggered = Value('b', False)  # 초기화 상태를 추적하는 플래그

    def conditional_callback():
        with is_ready.get_lock():
            if is_ready.value and not has_triggered.value:  # 초기화 시 한 번만 실행
                print("콜백 함수 호출")
                ir_disconnected_callback(ir_queue)
                has_triggered.value = True  # 이후에는 실행되지 않도록 설정
    conditional_callback()
    return ir_sensor

# 주석 처리된 코드는 실제 하드웨어에서 IR 센서 동작 코드
# def setup_ir_sensor(queue, is_ready):
#     ir_sensor = Button(IR_PIN, pull_up=True)
#     def conditional_callback():
#         with is_ready.get_lock():
#             if is_ready.value:
#                 ir_disconnected_callback(queue)
#     ir_sensor.when_pressed = conditional_callback
#     return ir_sensor

if __name__ == "__main__":
    from multiprocessing import Queue, Value
    queue = Queue()
    is_ready = Value('b', False)
    try:
        ir_sensor = setup_ir_sensor(queue, is_ready)
        print("IR sensor ready")
        while True:
            pass
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