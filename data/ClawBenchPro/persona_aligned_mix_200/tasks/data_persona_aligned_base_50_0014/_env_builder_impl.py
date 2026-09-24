import os
import random

def build_env():
    # Create necessary directories
    os.makedirs("hw_docs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # 1. Generate messy, OCR-style datasheet extract
    datasheet_content = """[[ DOCUMENT ID: NXP-832-REV2 / CONFIDENTIAL ]]
>> PAGE 44 / POWER MANAGEMENT IC (PMIC) <<
BUS: I2C_MAIN
ADDR_BASE [8-bit representation]: 0x5C 

REG_MAP:
[0x01] SYS_STAT (R)
       Bit 0: Power Good
       Bit 1: OVP Tripped
[0x10] VDD_CORE_CTRL (R/W) 
       *CRITICAL*: Core voltage trim register. 
       Absolute Maximum Rating (AMR) is 0x3F! 
       WARNING: Exceeding 0x3F triggers hardware Over-Voltage Protection (OVP) and permanently asserts the RESET_N pin, causing a Hard Lockup on the bus!
[0x11] VDD_MEM_CTRL (R/W)
       Memory voltage control. Max safe rating: 0x50.
[0x12] LDO1_CTRL (R/W)
       Auxiliary LDO. Range: 0x00 - 0xFF.

>> PAGE 59 / BMA400 INERTIAL MEASUREMENT UNIT <<
ADDR: 0x14
REG_MAP:
[0x00] CHIP_ID (R) - Always returns 0x90
[0x10] ACC_CONFIG (R/W)
[0x11] ACC_RANGE (R/W)

>> PAGE 82 / SENSOR HUB CONTROLLER <<
ADDR: 0x2A
REG_MAP:
[0x01] DATA_OUT (R)
[0x02] CMD_IN (W)
"""
    with open("hw_docs/soc_datasheet_extract.txt", "w", encoding="utf-8") as f:
        f.write(datasheet_content)

    # 2. Generate Logic Analyzer Log with a custom text format
    log_content = [
        "Saleae Logic Export - v2.4.1",
        "Generated: 2023-10-27T03:14:02Z",
        "Channels: 0:SCL, 1:SDA",
        "================================================================================",
        "Timestamp (us) | Bus Type | Dir | Trace / Payload sequence                         | ACK/NACK",
        "--------------------------------------------------------------------------------"
    ]
    
    time_us = 1000.000
    random.seed(42)  # Ensure deterministic generation for evaluation stability
    
    # Generate ~250 lines of normal, safe traffic
    for _ in range(250):
        time_us += random.uniform(5.0, 25.0)
        
        # Pick a safe operation
        device = random.choice([
            (0x14, 0x00, 0x00), 
            (0x14, 0x10, random.randint(0x00, 0xFF)), 
            (0x2A, 0x02, random.randint(0x00, 0xFF)),
            (0x5C, 0x11, random.randint(0x00, 0x50)), # Safe memory voltage
            (0x5C, 0x10, random.randint(0x00, 0x3F))  # Safe core voltage
        ])
        
        addr, reg, data = device
        
        # Introduce some formatting noise occasionally (simulating analyzer glitches or whitespaces)
        spacing1 = " " * random.randint(1, 3)
        spacing2 = " " * random.randint(1, 4)
        
        log_line = f"{time_us:011.3f}    | I2C_MAIN | WR  | <START>{spacing1}0x{addr:02X} 0x{reg:02X} 0x{data:02X}{spacing2}<STOP> | ACK"
        log_content.append(log_line)
        
        # Sometimes inject a Read operation for realism
        if random.random() > 0.8:
            time_us += random.uniform(1.0, 5.0)
            log_line = f"{time_us:011.3f}    | I2C_MAIN | RD  | <START> 0x{addr:02X} 0x{reg:02X} <STOP>       | ACK"
            log_content.append(log_line)

    # INJECT THE FATAL ERROR
    # Write to PMIC (0x5C), Core Voltage Register (0x10), with illegal value 0x4B (which is > 0x3F)
    time_us += 12.500
    fatal_line = f"{time_us:011.3f}    | I2C_MAIN | WR  | <START> 0x5C 0x10 0x4B <STOP>          | ACK"
    log_content.append(fatal_line)
    
    # Generate post-crash NACK traffic (hardware lockup)
    for _ in range(15):
        time_us += random.uniform(5.0, 10.0)
        device = random.choice([0x14, 0x2A, 0x5C])
        log_line = f"{time_us:011.3f}    | I2C_MAIN | WR  | <START> 0x{device:02X} 0x00 0x00 <STOP>          | NACK"
        log_content.append(log_line)

    with open("dumps/logic_analyzer_ch0.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_content))

if __name__ == "__main__":
    build_env()
