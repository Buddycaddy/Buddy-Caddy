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





# 처음부터 다시 수정하기 전 코드들

# def calculate_speed(ir_time, vibration_time, distance_m=2.0):
#     """
#     IR 센서 감지 시각과 진동 감지 시각의 차이를 바탕으로 속도를 계산합니다.
#     :param ir_time: IR 센서 감지 시각 (timestamp)
#     :param vibration_time: 진동 센서 감지 시각 (timestamp)
#     :param distance_m: IR 센서에서 네트까지 거리 (기본값 2미터)
#     :return: km/h 단위의 속도
#     """
#     time_diff = vibration_time - ir_time
#     if time_diff <= 0:
#         return 0.0  # 시간 역전 또는 오차 방지

#     speed_mps = distance_m / time_diff  # m/s
#     speed_kmph = speed_mps * 3.6        # km/h로 변환
#     return round(speed_kmph, 2)





# # import json

# # def calculate_speed(ir_timestamp, vib_timestamp, distance=3.0):
# #     if vib_timestamp > ir_timestamp:
# #         time_diff = vib_timestamp - ir_timestamp
# #         speed = distance / time_diff
# #         return {"speed": speed}
# #     return {"speed": None}

# # if __name__ == "__main__":
# #     test_data = {"ir_timestamp": 1634567890.123, "vib_timestamp": 1634567890.223}
# #     result = calculate_speed(test_data["ir_timestamp"], test_data["vib_timestamp"])
# #     print(json.dumps(result))