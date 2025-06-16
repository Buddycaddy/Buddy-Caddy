import RPi.GPIO as GPIO
import time
import json

IR_PIN = 17

def ir_callback(channel):
    timestamp = time.time()
    print(json.dumps({"event": "ir_trigger", "timestamp": timestamp}))

def setup_ir_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(IR_PIN, GPIO.FALLING, callback=ir_callback, bouncetime=200)

if __name__ == "__main__":
    try:
        setup_ir_sensor()
        print("IR sensor ready")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()





# 처음부터 다시 수정하기 전 코드들

# import time
# import datetime
# import threading

# try:
#     import RPi.GPIO as GPIO
#     IS_PI = True
# except ImportError:
#     IS_PI = False

# IR_PIN = 17

# def setup_ir_sensor(queue, simulate=False):
#     if simulate or not IS_PI:
#         # 시뮬레이션 모드: 3~6초 간격으로 감지된 것처럼 이벤트 발생
#         def simulate_ir():
#             while True:
#                 time.sleep(3 + (time.time() % 3))
#                 timestamp = datetime.datetime.now().timestamp()
#                 queue.put({"event": "ir_trigger", "timestamp": timestamp})
#         threading.Thread(target=simulate_ir, daemon=True).start()
#     else:
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#         def ir_callback(channel):
#             timestamp = datetime.datetime.now().timestamp()
#             queue.put({"event": "ir_trigger", "timestamp": timestamp})

#         GPIO.add_event_detect(IR_PIN, GPIO.FALLING, callback=ir_callback, bouncetime=200)





# # import RPi.GPIO as GPIO
# # import time
# # import json

# # IR_PIN = 17

# # def ir_callback(channel):
# #     timestamp = time.time()
# #     print(json.dumps({"event": "ir_trigger", "timestamp": timestamp}))

# # def setup_ir_sensor():
# #     GPIO.setmode(GPIO.BCM)
# #     GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# #     GPIO.add_event_detect(IR_PIN, GPIO.FALLING, callback=ir_callback, bouncetime=200)

# # if __name__ == "__main__":
# #     try:
# #         setup_ir_sensor()
# #         print("IR sensor ready")
# #         while True:
# #             time.sleep(1)
# #     except KeyboardInterrupt:
# #         GPIO.cleanup()