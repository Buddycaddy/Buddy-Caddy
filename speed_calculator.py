import json

def calculate_speed(ir_timestamp, vib_timestamp, distance=3.0):
    if vib_timestamp > ir_timestamp:
        time_diff = vib_timestamp - ir_timestamp
        speed = distance / time_diff
        return {"speed": speed}
    return {"speed": None}

if __name__ == "__main__":
    test_data = {"ir_timestamp": 1634567890.123, "vib_timestamp": 1634567890.223}
    result = calculate_speed(test_data["ir_timestamp"], test_data["vib_timestamp"])
    print(json.dumps(result))