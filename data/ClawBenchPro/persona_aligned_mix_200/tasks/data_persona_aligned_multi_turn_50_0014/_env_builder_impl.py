import os
import argparse
import json
import random

def build_turn_1():
    os.makedirs("datasheets", exist_ok=True)
    os.makedirs("logic_logs", exist_ok=True)
    
    # 传感器A手册 (SPI，电源监控)
    sensor_a = {
        "name": "PWR_Monitor_SPI",
        "interface": "SPI",
        "registers": {
            "0x10": "Voltage_High_Byte",
            "0x11": "Voltage_Low_Byte",
            "0x12": "Current_High_Byte",
            "0x13": "Current_Low_Byte"
        },
        "formulas": {
            "Voltage_V": "(High_Byte << 8 | Low_Byte) * 0.01",
            "Current_A": "(High_Byte << 8 | Low_Byte) * 0.005",
            "Power_W": "Voltage_V * Current_A"
        },
        "normal_range": {
            "Voltage_V": [4.8, 5.2],
            "Power_W": [0.0, 12.0]
        }
    }
    with open("datasheets/sensor_a_reg.json", "w", encoding="utf-8") as f:
        json.dump(sensor_a, f, indent=4)
        
    # 传感器B手册 (I2C，温湿度监控)
    sensor_b = {
        "name": "Env_Monitor_I2C",
        "interface": "I2C",
        "address": "0x44",
        "registers": {
            "0x00": "Temperature_Raw",
            "0x01": "Humidity_Raw"
        },
        "formulas": {
            "Temperature_C": "Raw_Value * 0.5 - 20",
            "Humidity_RH": "Raw_Value"
        },
        "normal_range": {
            "Temperature_C": [-10, 60]
        }
    }
    with open("datasheets/sensor_b_reg.json", "w", encoding="utf-8") as f:
        json.dump(sensor_b, f, indent=4)
        
    # 生成 Day 1 的总线日志
    with open("logic_logs/bus_trace_day1.log", "w", encoding="utf-8") as f:
        f.write("--- LOGIC ANALYZER EXPORT V1.2 ---\n")
        f.write("TIMESTAMP | BUS | ADDR/DEV | ACTION | REG | VAL\n")
        
        time_sec = 0
        for i in range(1, 50):
            time_sec += random.randint(10, 60)
            mins = time_sec // 60
            secs = time_sec % 60
            ts = f"08:{mins:02d}:{secs:02d}"
            
            # 制造正常的SPI数据, 电压稳在 5.0V (0x01F4 = 500)
            f.write(f"{ts} | SPI | CS0 | READ | 0x10 | 0x01\n")
            f.write(f"{ts} | SPI | CS0 | READ | 0x11 | 0xF4\n")
            
            # 电流从 1A 缓慢上升到 1.8A (200到360 -> 0x00C8 到 0x0168)
            curr = 200 + i * 3
            f.write(f"{ts} | SPI | CS0 | READ | 0x12 | 0x{curr >> 8:02X}\n")
            f.write(f"{ts} | SPI | CS0 | READ | 0x13 | 0x{curr & 0xFF:02X}\n")
            
            # 制造干扰 I2C 设备
            if i % 3 == 0:
                f.write(f"{ts} | I2C | 0x55 | WRITE | 0x0A | 0xFF\n")
                
            # 制造正常的I2C温度数据，缓慢上升，RAW从 90 到 110 (计算后温度为 25 到 35度，完全正常)
            temp_raw = 90 + i // 2
            f.write(f"{ts} | I2C | 0x44 | READ | 0x00 | 0x{temp_raw:02X}\n")
            f.write(f"{ts} | I2C | 0x44 | READ | 0x01 | 0x2A\n")


def build_turn_2():
    # 注意：执行 turn_2 时，turn_1 的文件已经存在，不要清空工作区
    with open("update_notice.txt", "w", encoding="utf-8") as f:
        f.write("【采购部加急通知】\n")
        f.write("现场批次为 SN-8000 后的网关，其 I2C 温度传感器更换为了廉价兼容型号（地址仍为 0x44）。\n")
        f.write("由于传感器的热敏元件特性变更，请研发部门注意，0x00 寄存器的温度计算公式必须修改为：\n")
        f.write("Temperature_C = Raw_Value * 1.5 - 60 \n")
        f.write("请在后续日志分析和排查中，以此新公式为准！\n")
        
    os.makedirs("logic_logs", exist_ok=True)
    with open("logic_logs/bus_trace_crash_day2.log", "w", encoding="utf-8") as f:
        f.write("--- LOGIC ANALYZER EXPORT V1.2 ---\n")
        f.write("TIMESTAMP | BUS | ADDR/DEV | ACTION | REG | VAL\n")
        
        time_sec = 0
        for i in range(1, 30):
            time_sec += random.randint(5, 15)
            mins = time_sec // 60
            secs = time_sec % 60
            ts = f"09:{mins:02d}:{secs:02d}"
            
            # SPI 电源轻微波动但仍合法 (5.0V, 2.2A -> Power = 11W，在 12W 限制内)
            f.write(f"{ts} | SPI | CS0 | READ | 0x10 | 0x01\n")
            f.write(f"{ts} | SPI | CS0 | READ | 0x11 | 0xF4\n")
            curr = 440 # 440 * 0.005 = 2.2A
            f.write(f"{ts} | SPI | CS0 | READ | 0x12 | 0x{curr >> 8:02X}\n")
            f.write(f"{ts} | SPI | CS0 | READ | 0x13 | 0x{curr & 0xFF:02X}\n")
            
            # I2C 温度数据。
            # 这里是毒药选项：
            # RAW 值为 90 左右，如果按昨天的旧公式 90 * 0.5 - 20 = 25度（完全正常）。
            # 但是按今天的更新公式： 90 * 1.5 - 60 = 75度！这超出了手册规定的 60 度上限。
            # 随着运行，RAW 值升到了 95 (新公式计算下达到 82.5度，导致最终热保护锁死)
            temp_raw = 85 + i // 3
            f.write(f"{ts} | I2C | 0x44 | READ | 0x00 | 0x{temp_raw:02X}\n")
            f.write(f"{ts} | I2C | 0x44 | READ | 0x01 | 0x2A\n")
            
        # 崩溃前最后一刻
        f.write("09:07:11 | I2C | 0x44 | READ | 0x00 | 0x60\n")  # 0x60 = 96 -> 新公式 84度
        f.write("09:07:12 | SYS | SYSTEM_HALT | KERNEL_PANIC | N/A | N/A\n")


def build_turn_3():
    # 注意：执行 turn_3 时，前两轮文件存在
    hw_constraints = {
        "version": "1.0_patch",
        "critical_limits": {
            "Max_Safe_Temp_C": 65.0,
            "Max_Safe_Power_W": 10.0
        },
        "instruction": "If limits exceeded, device must reset or throttle."
    }
    with open("hw_constraints.json", "w", encoding="utf-8") as f:
        json.dump(hw_constraints, f, indent=4)
        
    fw_code = """#include <stdio.h>
#include "hardware_hal.h"

// 传感器读取上下文
extern uint16_t current_power_raw;
extern uint8_t current_temp_raw;

void system_health_monitor() {
    float power_w = 0.0;
    float temp_c = 0.0;
    
    // TODO: 根据传感器数据手册和最新的修正公式计算当前的功率和温度
    
    // TODO: 插入异常保护阈值判断
    // if (...) {
    //     trigger_system_reset();
    // }
    
    feed_watchdog();
}
"""
    with open("fw_template.c", "w", encoding="utf-8") as f:
        f.write(fw_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
