import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json



#진동 센서  output 1 or 0 예상

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