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