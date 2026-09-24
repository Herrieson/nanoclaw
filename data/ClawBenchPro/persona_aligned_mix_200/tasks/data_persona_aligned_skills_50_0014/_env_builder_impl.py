import os
import random
import base64

def build_env():
    # Create necessary directories
    os.makedirs("hw_docs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # Note: hw_docs is deliberately left empty to force database queries.

    # 1. Generate Logic Analyzer Log data
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
        # Note: 0x5C is the NXP-832-REV2, 0x10 is core voltage (max 0x3F), 0x11 is memory (max 0x50)
        device = random.choice([
            (0x14, 0x00, 0x00), 
            (0x14, 0x10, random.randint(0x00, 0xFF)), 
            (0x2A, 0x02, random.randint(0x00, 0xFF)),
            (0x5C, 0x11, random.randint(0x00, 0x50)), # Safe memory voltage
            (0x5C, 0x10, random.randint(0x00, 0x3F))  # Safe core voltage
        ])
        
        addr, reg, data = device
        
        spacing1 = " " * random.randint(1, 3)
        spacing2 = " " * random.randint(1, 4)
        
        log_line = f"{time_us:011.3f}    | I2C_MAIN | WR  | <START>{spacing1}0x{addr:02X} 0x{reg:02X} 0x{data:02X}{spacing2}<STOP> | ACK"
        log_content.append(log_line)
        
        # Inject Read operation occasionally
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

    raw_text = "\n".join(log_content)
    
    # Obfuscate the text into a proprietary ".salb" format to force tool usage
    encoded_bytes = base64.b64encode(raw_text.encode("utf-8"))
    
    with open("dumps/logic_analyzer_ch0.salb", "wb") as f:
        f.write(encoded_bytes)

if __name__ == "__main__":
    build_env()
