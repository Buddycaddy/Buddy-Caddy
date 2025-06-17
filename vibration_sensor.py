# 실제 라즈베리 파이에서 작동하는 코드
# import time
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
# import json

# def setup_vibration_sensor():
#     i2c = busio.I2C(board.SCL, board.SDA)
#     ads = ADS.ADS1115(i2c)
#     ads.data_rate = 250
#     return AnalogIn(ads, ADS.P0)

# def detect_vibration(chan, threshold=1.0, is_ready=None):
#     if is_ready:
#         with is_ready.get_lock():
#             if not is_ready.value:
#                 return None
#     if chan.voltage > threshold:
#         return {"source": "vibration_sensor", "event": "vibration_trigger", "timestamp": time.time()}
#     return None

# if __name__ == "__main__":
#     from multiprocessing import Value
#     chan = setup_vibration_sensor()
#     is_ready = Value('b', True)
#     while True:
#         result = detect_vibration(chan, is_ready=is_ready)
#         if result:
#             print(json.dumps(result))
#         time.sleep(0.004)


# 전체 프로세스 동작 확인을 위한 진동 센서 모듈 코드
import time
import json
from multiprocessing import Queue, Value

class MockAnalogIn:
    def __init__(self):
        self.voltage = 0.0  # 초기값 설정

    def set_voltage(self, value):
        self.voltage = value  # 테스트를 위해 전압 설정

def setup_vibration_sensor():
    # 실제 I2C 대신 MockAnalogIn을 반환
    return MockAnalogIn()


def detect_vibration(queue,chan, threshold=1.0, is_ready=None):
    has_triggered = Value('b', False)  # 초기화 상태를 추적하는 플래그
    chan.set_voltage(1.5)  # 초기 전압 설정
    def conditional_callback():
        with is_ready.get_lock():
            if is_ready.value and not has_triggered.value:  # 초기화 시 한 번만 실행
                if chan.voltage > threshold:
                    print("진동 센서 신호 전송")
                    has_triggered.value = True  # 이후에는 실행되지 않도록 설정
                    queue.put({"source": "vibration_sensor", "event": "vibration_trigger", "timestamp": time.time()})
        return None

    return conditional_callback()

#실제 라즈베이 파이에서 작동하는 코드
# def detect_vibration(chan, threshold=1.0, is_ready=None):
#     if is_ready:
#         with is_ready.get_lock():
#             if not is_ready.value:
#                 return None
#     if chan.voltage > threshold:
#         return {"source": "vibration_sensor", "event": "vibration_trigger", "timestamp": time.time()}
#     return None

if __name__ == "__main__":
    from multiprocessing import Value
    chan = setup_vibration_sensor()
    is_ready = Value('b', True)

    # 테스트용으로 전압을 설정하여 디버깅
    test_voltages = [0.5, 1.2, 0.8, 1.5]  # 테스트 전압 값
    for voltage in test_voltages:
        chan.set_voltage(voltage)  # MockAnalogIn에 전압 설정
        result = detect_vibration(chan, is_ready=is_ready)
        if result:
            print(json.dumps(result))
        time.sleep(0.004)