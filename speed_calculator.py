import json

def calculate_speed(ir_timestamp, vib_timestamp, distance=1.5):
    if vib_timestamp > ir_timestamp:
        time_diff = vib_timestamp - ir_timestamp
        speed_mps = distance / time_diff  # m/s
        speed_kmph = speed_mps * 3.6      # km/h
        print("속도 계산 완료")
        print(f"IR Timestamp: {ir_timestamp}, Vibration Timestamp: {vib_timestamp}")
        print(f"Time Difference: {time_diff} seconds")
        print(f"Speed: {speed_kmph} km/h")

    
        return {"source": "speed_calculator", "speed": round(speed_kmph, 2)}
    return {"source": "speed_calculator", "speed": None}

if __name__ == "__main__":
    #예시 설정
    test_data = {"ir_timestamp": 1634567890.123, "vib_timestamp": 1634567890.223}
    result = calculate_speed(test_data["ir_timestamp"], test_data["vib_timestamp"])
    print(json.dumps(result))
