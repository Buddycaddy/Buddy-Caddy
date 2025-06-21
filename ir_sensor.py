import RPi.GPIO as GPIO
from gpiozero import Button
# from gpiozero import Button, Device
# from gpiozero.pins.mock import MockFactory
from multiprocessing import Queue, Value
import time

# Pin Factory를 MockFactory로 설정 (PC 테스트용)
# Device.pin_factory = MockFactory()

IR_PINS = [18, 23, 24]
#18 -> 후측 하단
#23 -> 전측 하단
#24 -> 후측 상단
# def ir_disconnected_callback(queue, pin):
#     print(f"IR sensor {pin} 전송")
#     queue.put({"source": "ir_sensor", "event": "ir_trigger", "pin": pin, "timestamp": time.time()})



def setup_ir_sensors(ir_queue, is_ready):
    """IR 센서 초기화"""
    GPIO.setmode(GPIO.BCM)  # BCM 모드 사용
    GPIO.setwarnings(False)

    def ir_disconnected_callback(queue, pin):
        print(f"IR sensor {pin} 전송")
        queue.put({"source": "ir_sensor", "event": "ir_trigger", "pin": pin, "timestamp": time.time()})
    
    for pin in IR_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 풀업 저항 사용
        # 콜백에 큐와 핀을 넘기려면 람다 또는 functools.partial 사용
        GPIO.add_event_detect(
            pin,
            GPIO.FALLING,
            callback=lambda channel, p=pin: ir_disconnected_callback(ir_queue, p),
            bouncetime=20
        )
        print(f"IR sensor on pin {pin} initialized")

if __name__ == "__main__":
    queue = Queue()
    is_ready = Value('b', True)
    try:
        sensors = setup_ir_sensors(queue, is_ready)
        print("IR sensors ready")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Exiting program")


