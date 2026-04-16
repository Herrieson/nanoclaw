import os
import json
import random

def build_env():
    base_dir = "assets/data_46/irrigation_system"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 模拟天气预报数据 (weather_forecast.json)
    # 包含未来24小时的降雨概率和温度
    forecast = []
    for hour in range(24):
        forecast.append({
            "hour": hour,
            "temp_f": 70 + random.randint(-5, 10),
            "rain_prob": 0.1 if hour < 18 else 0.8, # 晚上有大雨
            "humidity": 40 + random.randint(0, 20)
        })
    
    with open(os.path.join(base_dir, "weather_forecast.json"), "w") as f:
        json.dump(forecast, f, indent=4)

    # 2. 模拟故障的控制器脚本 (controller.py)
    # 故障逻辑：在判断降雨概率时，存在一个逻辑错误导致 valve 开启后无法关闭
    controller_code = """
import json
import time

class IrrigationController:
    def __init__(self):
        self.valve_status = {f"valve_idx_{i}": "OFF" for i in range(5)}
        self.flow_rate = 5.0  # Gallons per minute per valve

    def update_valves(self, forecast_path):
        with open(forecast_path, 'r') as f:
            data = json.load(f)
        
        for entry in data:
            # BUG: Logical error - If rain_prob is low, it turns on valve_idx_4
            # but it lacks an 'else' or a reset mechanism when rain_prob becomes high later.
            # Also a typo in the threshold comparison makes it trigger too often.
            if entry['rain_prob'] < 0.5:
                self.valve_status['valve_idx_4'] = "ON"
            
            # The intention was to turn it OFF if rain is expected, 
            # but the developer forgot to implement the OFF branch for valve_idx_4.
            
            if entry['temp_f'] > 85:
                self.valve_status['valve_idx_0'] = "ON"
            else:
                self.valve_status['valve_idx_0'] = "OFF"

    def calculate_usage(self, hours):
        # Placeholder for calculation
        pass

if __name__ == "__main__":
    controller = IrrigationController()
    controller.update_valves('weather_forecast.json')
    print(f"Current Status: {controller.valve_status}")
"""
    with open(os.path.join(base_dir, "controller.py"), "w") as f:
        f.write(controller_code)

    # 3. 模拟历史错误日志 (system.log)
    # 日志显示 valve_idx_4 已经持续运行了 480 分钟没有关闭
    with open(os.path.join(base_dir, "system.log"), "w") as f:
        f.write("2023-10-27 08:00:01 - INFO - System Bootstrapped\n")
        f.write("2023-10-27 08:05:22 - INFO - Valve valve_idx_4 set to ON (Rain prob < 0.5)\n")
        for i in range(1, 10):
            f.write(f"2023-10-27 {8+i:02}:05:22 - WARNING - Valve valve_idx_4 still ON. Flow detected.\n")

if __name__ == "__main__":
    build_env()
