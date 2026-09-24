import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("sim_logs/dma_burst_01", exist_ok=True)
    os.makedirs("sim_logs/dma_burst_02", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 构建复杂的干扰数据，需要通过多个条件(周期1000-5000, MASTER_1/3, VALID=1, DATA含X或Z)过滤
    waves_01 = [
        "Cycle, Master, Module, Address, Valid, Data",
        "0999, MASTER_1, UART_CTRL, 0x1000, 1, 8'bXXXX",    # 坑：周期不到1000
        "1050, MASTER_1, SPI_HOST, 0x2000, 1, 8'b110X",     # 命中：SPI_HOST
        "1800, MASTER_1, SPI_HOST, 0x2008, 0, 8'bXXXX",     # 坑：VALID=0
        "3000, MASTER_2, MEM_CTRL, 0x4000, 1, 8'bZZZZ",     # 坑：MASTER_2不关心
        "4200, MASTER_3, I2C_HOST, 0x5000, 1, 8'b101Z",     # 命中：I2C_HOST
        "4999, MASTER_1, I2C_HOST, 0x5004, 1, 8'b1111",     # 坑：无X或Z
        "5001, MASTER_1, USB_CTRL, 0x6000, 1, 8'bXXXX"      # 坑：周期超5000
    ]
    with open("sim_logs/dma_burst_01/waves.txt", "w") as f:
        f.write("\n".join(waves_01) + "\n")
        
    waves_02 = [
        "Cycle, Master, Module, Address, Valid, Data",
        "1200, MASTER_3, GPIO_PORT, 0x7000, 1, 8'b0000",    # 正常
        "2500, MASTER_1, PWM_CTRL, 0x8000, 1, 8'b01XZ",     # 命中：PWM_CTRL
        "4900, MASTER_3, ADC_IF, 0x9000, 1, 8'b0011",       # 正常
        "6000, MASTER_3, PWM_CTRL, 0x8008, 1, 8'bZZZZ"      # 坑：周期超出
    ]
    with open("sim_logs/dma_burst_02/waves.txt", "w") as f:
        f.write("\n".join(waves_02) + "\n")

def build_turn_2():
    os.makedirs("sim_logs/interrupt_ctrl", exist_ok=True)
    # Turn 1 查出的问题模块应为：SPI_HOST, I2C_HOST, PWM_CTRL
    # 本轮需要结合第一轮的模块名和 1000-5000 的窗口
    irq_logs = [
        ["Cycle", "Source_Module", "Interrupt_ID", "INT_ERR", "ACK"],
        [1100, "SPI_HOST", 14, 1, 0],    # 命中：ID 14
        [1500, "SPI_HOST", 15, 1, 1],    # 坑：ACK=1
        [2000, "MEM_CTRL", 18, 1, 0],    # 坑：MEM_CTRL 在第一轮没被定性为问题模块（因为它是MASTER_2触发的）
        [2500, "I2C_HOST", 22, 1, 0],    # 命中：ID 22
        [3000, "PWM_CTRL", 25, 0, 0],    # 坑：INT_ERR=0
        [4500, "PWM_CTRL", 28, 1, 0],    # 命中：ID 28
        [5500, "I2C_HOST", 30, 1, 0],    # 坑：周期超出 5000
    ]
    with open("sim_logs/interrupt_ctrl/irq_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(irq_logs)

def build_turn_3():
    os.makedirs("patches", exist_ok=True)
    # 目标：覆盖模块 [SPI_HOST, I2C_HOST, PWM_CTRL]，覆盖中断 [14, 22, 28]
    # 预算约束：<= 120ps
    
    # 陷阱1：看似一键修复所有，但超预算
    patch_all_in_one = {
        "id": "PATCH_OMEGA",
        "fixes_modules": ["SPI_HOST", "I2C_HOST", "PWM_CTRL"],
        "fixes_interrupts": [14, 22, 28],
        "delay_ps": 130 
    }
    
    # 补丁组合设计：寻找最优解 (A + B)
    patch_a = {
        "id": "PATCH_ALPHA",
        "fixes_modules": ["SPI_HOST", "PWM_CTRL"],
        "fixes_interrupts": [14],
        "delay_ps": 45
    }
    
    patch_b = {
        "id": "PATCH_BETA",
        "fixes_modules": ["I2C_HOST"],
        "fixes_interrupts": [22, 28],
        "delay_ps": 45
    }
    # ALPHA + BETA = 90ps，完全覆盖，最优解。

    # 干扰补丁
    patch_c = {
        "id": "PATCH_GAMMA",
        "fixes_modules": ["SPI_HOST", "I2C_HOST"],
        "fixes_interrupts": [14, 22],
        "delay_ps": 80
    }
    
    patch_d = {
        "id": "PATCH_DELTA",
        "fixes_modules": ["PWM_CTRL"],
        "fixes_interrupts": [28],
        "delay_ps": 50
    }
    # GAMMA + DELTA = 130ps，覆盖但超预算。
    
    patch_e = {
        "id": "PATCH_EPSILON",
        "fixes_modules": ["SPI_HOST"],
        "fixes_interrupts": [14, 28],
        "delay_ps": 30
    }
    
    patch_f = {
        "id": "PATCH_ZETA",
        "fixes_modules": ["I2C_HOST", "PWM_CTRL"],
        "fixes_interrupts": [22],
        "delay_ps": 70
    }
    # EPSILON + ZETA = 100ps，覆盖所有。 虽然合法，但 100ps > 90ps，不是最省的。
    
    patches = [patch_all_in_one, patch_a, patch_b, patch_c, patch_d, patch_e, patch_f]
    
    for p in patches:
        with open(f"patches/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

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
