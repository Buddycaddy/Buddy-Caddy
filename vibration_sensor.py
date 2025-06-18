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


def detect_vibration(vib_queue,impact_queue,is_ready,chan, threshold=1.0):
    has_triggered_speed = Value('b', False)  # 속도 계산 플래그
    has_triggered_impact = Value('b', False)  # 임팩트 분석 플래그

    def conditional_callback():
        with is_ready.get_lock():
            if is_ready.value:
                if not has_triggered_speed.value and chan.voltage > threshold:
                    print("진동 센서 신호 전송 - 속도 계산")
                    has_triggered_speed.value = True  # 이후에는 실행되지 않도록 설정
                    vib_queue.put({"source": "vibration_sensor", "event": "vibration_trigger", "timestamp": time.time(), "action": "speed"})       

                if not has_triggered_impact.value and chan.voltage > threshold:
                    print("진동 센서 신호 전송 - 임팩트 분석")
                    has_triggered_impact.value = True  # 이후에는 실행되지 않도록 설정
                    impact_queue.put({"source": "vibration_sensor", "event": "vibration_trigger", "timestamp": time.time(), "action": "impact"})

    return conditional_callback()

#실제 라즈베이 파이에서 작동하는 코드
# def detect_vibration(chan, threshold=1.0, is_ready=None):
#     if is_ready:ㄴ
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