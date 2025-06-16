import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json

def setup_vibration_sensor():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.data_rate = 250
    return AnalogIn(ads, ADS.P0)

def detect_vibration(chan, threshold=1.0):
    if chan.voltage > threshold:
        return {"event": "vibration_trigger", "timestamp": time.time()}
    return None

if __name__ == "__main__":
    chan = setup_vibration_sensor()
    while True:
        result = detect_vibration(chan)
        if result:
            print(json.dumps(result))
        time.sleep(0.004)  # 250Hz




# 처음부터 다시 수정하기 전 코드들

# import time
# import datetime
# import threading

# try:
#     import RPi.GPIO as GPIO
#     IS_PI = True
# except ImportError:
#     IS_PI = False

# VIBRATION_PIN = 27

# def setup_vibration_sensor():
#     if not IS_PI:
#         return None
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     return VIBRATION_PIN

# def detect_vibration(pin):
#     if not IS_PI or pin is None:
#         return False
#     return GPIO.input(pin) == GPIO.HIGH

# def vibration_sensor_process(queue, simulate=False):
#     if simulate or not IS_PI:
#         def simulate_vibration():
#             while True:
#                 time.sleep(5 + (time.time() % 4))
#                 timestamp = datetime.datetime.now().timestamp()
#                 queue.put({"event": "vibration_trigger", "timestamp": timestamp})
#         threading.Thread(target=simulate_vibration, daemon=True).start()
#         while True:
#             time.sleep(1)
#     else:
#         pin = setup_vibration_sensor()
#         try:
#             while True:
#                 if detect_vibration(pin):
#                     timestamp = datetime.datetime.now().timestamp()
#                     queue.put({"event": "vibration_trigger", "timestamp": timestamp})
#                 time.sleep(0.004)
#         except KeyboardInterrupt:
#             GPIO.cleanup()





# # import RPi.GPIO as GPIO
# # import time
# # import datetime

# # VIBRATION_PIN = 27  # 사용할 핀 번호 (실제 배선에 따라 변경 필요)

# # # 센서 설정 함수
# # def setup_vibration_sensor():
# #     GPIO.setmode(GPIO.BCM)
# #     GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# #     return VIBRATION_PIN

# # # 루프 내에서 센서 감지하는 함수
# # def detect_vibration(pin):
# #     return GPIO.input(pin) == GPIO.HIGH

# # # main.py에서 이 함수를 호출하면 됨
# # def vibration_sensor_process(queue):
# #     pin = setup_vibration_sensor()
# #     try:
# #         while True:
# #             if detect_vibration(pin):
# #                 timestamp = datetime.datetime.now().timestamp()
# #                 queue.put({"event": "vibration_trigger", "timestamp": timestamp})
# #             time.sleep(0.004)
# #     except KeyboardInterrupt:
# #         GPIO.cleanup()





# # import time
# # import board
# # import busio
# # import adafruit_ads1x15.ads1115 as ADS
# # from adafruit_ads1x15.analog_in import AnalogIn
# # import json

# # def setup_vibration_sensor():
# #     i2c = busio.I2C(board.SCL, board.SDA)
# #     ads = ADS.ADS1115(i2c)
# #     ads.data_rate = 250
# #     return AnalogIn(ads, ADS.P0)

# # def detect_vibration(chan, threshold=1.0):
# #     if chan.voltage > threshold:
# #         return {"event": "vibration_trigger", "timestamp": time.time()}
# #     return None

# # if __name__ == "__main__":
# #     chan = setup_vibration_sensor()
# #     while True:
# #         result = detect_vibration(chan)
# #         if result:
# #             print(json.dumps(result))
# #         time.sleep(0.004)  # 250Hz