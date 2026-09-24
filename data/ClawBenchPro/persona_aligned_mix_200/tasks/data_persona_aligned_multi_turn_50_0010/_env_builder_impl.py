import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("datasheets", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    
    # 模拟数据手册：IMU 寄存器
    with open("datasheets/IMU_regs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Register", "Name", "Access", "Expected_Init_Value"])
        writer.writerow(["0x1A", "CONFIG", "RW", "0x05"])
        writer.writerow(["0x2B", "GYRO_CONFIG", "RW", "0x11"])
        writer.writerow(["0x6B", "PWR_MGMT_1", "RW", "0x00"])
        writer.writerow(["0x75", "WHO_AM_I", "R", "0x68"])
        
    # 模拟数据手册：环境传感器寄存器
    with open("datasheets/Env_regs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Register", "Name", "Access", "Expected_Init_Value"])
        writer.writerow(["0xF4", "CTRL_MEAS", "RW", "0x27"])
        writer.writerow(["0xF5", "CONFIG", "RW", "0xA0"])
        writer.writerow(["0x01", "CALIB_00", "R", "0x00"])
        
    # 模拟逻辑分析仪导出的无结构 T1 初始崩溃日志
    with open("raw_logs/bus_trace_T1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Protocol", "Details"])
        # 设置干扰陷阱：EEPROM (0x50) 的报错，不属于 IMU 和 Env
        writer.writerow(["0.0010", "I2C", "Setup Write to [0x50] + ACK"])
        writer.writerow(["0.0011", "I2C", "Data [0x00] + NACK"]) 
        
        # IMU 初始化
        writer.writerow(["0.0020", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["0.0021", "I2C", "Data [0x1A] + ACK"])
        writer.writerow(["0.0022", "I2C", "Data [0x06] + ACK"]) # 陷阱BUG 1：应为 0x05
        
        writer.writerow(["0.0030", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["0.0031", "I2C", "Data [0x2B] + ACK"])
        writer.writerow(["0.0032", "I2C", "Data [0x11] + ACK"]) # 正常匹配
        
        writer.writerow(["0.0040", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["0.0041", "I2C", "Data [0x6B] + ACK"])
        writer.writerow(["0.0042", "I2C", "Data [0x01] + ACK"]) # 陷阱BUG 2：应为 0x00
        
        # Env 传感器初始化
        writer.writerow(["0.0050", "I2C", "Setup Write to [0x76] + ACK"])
        writer.writerow(["0.0051", "I2C", "Data [0xF4] + ACK"])
        writer.writerow(["0.0052", "I2C", "Data [0x27] + ACK"]) # 正常匹配
        
        writer.writerow(["0.0060", "I2C", "Setup Write to [0x76] + ACK"])
        writer.writerow(["0.0061", "I2C", "Data [0x01] + ACK"])
        writer.writerow(["0.0062", "I2C", "Data [0xFF] + NACK"]) # 陷阱BUG 3：强写只读寄存器

def build_turn_2():
    os.makedirs("raw_logs", exist_ok=True)
    # 模拟固件补丁后，混合 SPI/I2C 复杂时序的 T2 日志
    with open("raw_logs/bus_trace_T2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Protocol", "Details"])
        # 补丁：初始化的值已经被正确修复
        writer.writerow(["0.0020", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["0.0021", "I2C", "Data [0x1A] + ACK"])
        writer.writerow(["0.0022", "I2C", "Data [0x05] + ACK"]) # 修复完毕
        writer.writerow(["0.0040", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["0.0041", "I2C", "Data [0x6B] + ACK"])
        writer.writerow(["0.0042", "I2C", "Data [0x00] + ACK"]) # 修复完毕
        writer.writerow(["0.0050", "I2C", "Setup Write to [0x76] + ACK"])
        writer.writerow(["0.0051", "I2C", "Data [0xF4] + ACK"])
        writer.writerow(["0.0052", "I2C", "Data [0x27] + ACK"]) 
        # (已移除对 0x01 的非法写操作)
        
        # 干扰项：正常无害的 SPI 读取
        writer.writerow(["1.0000", "SPI", "CS Active"])
        writer.writerow(["1.0001", "SPI", "MOSI: 0x03"])
        writer.writerow(["1.0002", "SPI", "MOSI: 0x0B, 0x00, 0x10"])
        writer.writerow(["1.0003", "SPI", "MISO: 0x00, 0x11, 0x22"])
        writer.writerow(["1.0004", "SPI", "CS Inactive"])
        # 随后的 I2C 正常（未死机）
        writer.writerow(["1.0010", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["1.0011", "I2C", "Data [0x3B] + ACK"])
        
        # 致命操作 1
        writer.writerow(["1.2000", "SPI", "CS Active"])
        writer.writerow(["1.2001", "SPI", "MOSI: 0x03"])
        writer.writerow(["1.2002", "SPI", "MOSI: 0x0A, 0x12, 0x34"])
        writer.writerow(["1.2003", "SPI", "MISO: 0xFF, 0xFF, 0xFF"])
        writer.writerow(["1.2004", "SPI", "CS Inactive"])
        # 导致紧跟的 I2C 崩溃
        writer.writerow(["1.2010", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["1.2011", "I2C", "Data [0x3B] + NACK"]) # Crash
        
        # 干扰项 2：另一次正常 SPI
        writer.writerow(["1.5000", "SPI", "CS Active"])
        writer.writerow(["1.5001", "SPI", "MOSI: 0x03"])
        writer.writerow(["1.5002", "SPI", "MOSI: 0x0C, 0xAA, 0xBB"])
        writer.writerow(["1.5003", "SPI", "MISO: 0x01, 0x02, 0x03"])
        writer.writerow(["1.5004", "SPI", "CS Inactive"])
        
        # 致命操作 2
        writer.writerow(["1.8000", "SPI", "CS Active"])
        writer.writerow(["1.8001", "SPI", "MOSI: 0x03"])
        writer.writerow(["1.8002", "SPI", "MOSI: 0x0A, 0x15, 0x00"])
        writer.writerow(["1.8003", "SPI", "MISO: 0x00, 0x00, 0x00"])
        writer.writerow(["1.8004", "SPI", "CS Inactive"])
        # 导致紧跟的 I2C 崩溃
        writer.writerow(["1.8010", "I2C", "Setup Write to [0x68] + ACK"])
        writer.writerow(["1.8011", "I2C", "Data [0x3B] + NACK"]) # Crash

def build_turn_3():
    os.makedirs("config", exist_ok=True)
    
    # 模拟 Flash 内存映射表
    flash_map = {
      "sectors": [
        {"start": "0x0A0000", "end": "0x0AFFFF", "task": "Task_Audio_Stream"},
        {"start": "0x0B0000", "end": "0x0BFFFF", "task": "Task_Log_Flush"},
        {"start": "0x0C0000", "end": "0x0CFFFF", "task": "Task_OTA_Update"}
      ]
    }
    with open("config/flash_map.json", "w") as f:
        json.dump(flash_map, f, indent=2)
        
    # 模拟调度器，埋下时间窗口重叠引发灾难的伏笔
    # Task_IMU_Poll 窗口: 10 到 25
    # Task_Audio_Stream 窗口: 12 到 32 (完全重叠，必然撞车崩溃)
    # 解决此任务需要调整 Task_Audio_Stream 的 offset_ms 至 25 到 40 之间
    scheduler = {
      "tasks": [
        {"name": "Task_IMU_Poll", "offset_ms": 10, "duration_ms": 15},
        {"name": "Task_Audio_Stream", "offset_ms": 12, "duration_ms": 20},
        {"name": "Task_Log_Flush", "offset_ms": 60, "duration_ms": 10},
        {"name": "Task_OTA_Update", "offset_ms": 80, "duration_ms": 5}
      ]
    }
    with open("config/scheduler.json", "w") as f:
        json.dump(scheduler, f, indent=2)

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
