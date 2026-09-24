import os
import random
import base64
from datetime import datetime, timedelta

def build_env():
    """Builds the environment for data_persona_aligned_skills_50_0010"""
    os.makedirs('traces', exist_ok=True)
    os.makedirs('report', exist_ok=True)

    start_time = datetime(2024, 5, 12, 14, 20, 0, 0)
    current_time = start_time

    def advance_time(ms=1):
        nonlocal current_time
        current_time += timedelta(microseconds=ms * 1000 + random.randint(10, 100))
        return current_time.strftime("[%H:%M:%S.%f]")[:-3] + "]"

    def make_txn(addr_hex, is_read, reg_hex, data_hex_list, nack_at_data_idx=-1):
        lines = []
        lines.append(f"{advance_time()} [CH0] I2C START")
        
        addr_byte = (int(addr_hex, 16) << 1) | (1 if is_read else 0)
        lines.append(f"{advance_time()} [CH0] TX: {addr_byte:02X}")
        lines.append(f"{advance_time()} [CH0] RX: ACK")

        if reg_hex is not None:
            lines.append(f"{advance_time()} [CH0] TX: {reg_hex}")
            lines.append(f"{advance_time()} [CH0] RX: ACK")

        for i, data in enumerate(data_hex_list):
            if is_read:
                lines.append(f"{advance_time()} [CH0] RX: {data}")
                if i == len(data_hex_list) - 1 and nack_at_data_idx == -1:
                    lines.append(f"{advance_time()} [CH0] TX: NACK") 
                else:
                    lines.append(f"{advance_time()} [CH0] TX: ACK")
            else:
                lines.append(f"{advance_time()} [CH0] TX: {data}")
                if i == nack_at_data_idx:
                    lines.append(f"{advance_time()} [CH0] RX: NACK")
                    break 
                else:
                    lines.append(f"{advance_time()} [CH0] RX: ACK")

        lines.append(f"{advance_time()} [CH0] I2C STOP")
        return lines

    log_lines = []
    log_lines.append("=== SIGROK DECODE ENGINE V0.5.2 RAW DUMP ===")
    log_lines.append("=== PROTOCOL: I2C (FAST MODE 400KHZ) ===")
    log_lines.append(f"=== CAPTURE START: {start_time.isoformat()} ===")
    log_lines.append("-" * 50)

    # Noise: EEPROM Read
    for _ in range(2):
        log_lines.extend(make_txn('50', False, f"{random.randint(0, 255):02X}", []))
        log_lines.extend(make_txn('50', True, None, [f"{random.randint(0, 255):02X}" for _ in range(2)]))
        current_time += timedelta(milliseconds=12)

    # 干扰项 (Red Herring): PMIC-3400 (Address 0x34 -> Write 0x68) NACKing on 0x11
    log_lines.extend(make_txn('34', False, '10', ['FF']))
    log_lines.append(f"{advance_time()} [WARNING] I2C Device 0x34 responded with NACK during data payload.")
    log_lines.extend(make_txn('34', False, '11', ['80'], nack_at_data_idx=0)) 
    log_lines.extend(make_txn('34', False, '14', ['0F']))
    current_time += timedelta(milliseconds=45)

    log_lines.append(f"{advance_time()} --- SYS EVENT: GPIO_INT0 RISING EDGE (WAKEUP) ---")

    # Target: IMU-6800 Initialization sequence (Address 0x68 -> Write 0xD0)
    log_lines.extend(make_txn('68', False, '6B', ['00'])) # Pwr mgmt 1
    log_lines.extend(make_txn('68', False, '1A', ['03'])) # Config
    log_lines.extend(make_txn('68', False, '1B', ['18'])) # Gyro config

    # INTENTIONAL FATAL BUG INJECTION
    # Trying to write invalid data 0x7F to reserved register 0x2A for IMU.
    log_lines.append(f"{advance_time()} [FATAL] I2C Device 0x68 responded with NACK on reserved register!")
    log_lines.extend(make_txn('68', False, '2A', ['7F'], nack_at_data_idx=0))

    current_time += timedelta(milliseconds=5)
    log_lines.append(f"{advance_time()} --- SYS EVENT: I2C_ERR_INTERRUPT ---")
    log_lines.extend(make_txn('50', False, '00', ['01'])) 

    # Serialize and Obfuscate the log to force the agent to use the decoder skill
    raw_text = '\n'.join(log_lines) + '\n'
    b64_data = base64.b64encode(raw_text.encode('utf-8')).decode('utf-8')

    with open('traces/i2c_bus_raw.bin', 'w') as f:
        # Wrap in a fake binary header
        f.write(f"SALEAE_RAW_DUMP_V2\n{b64_data}\nEOF")

if __name__ == '__main__':
    build_env()
