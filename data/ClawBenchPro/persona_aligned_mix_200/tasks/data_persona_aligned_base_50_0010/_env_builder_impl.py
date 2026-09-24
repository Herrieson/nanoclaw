import os
import random
from datetime import datetime, timedelta

def build_env():
    """Builds the environment for data_persona_aligned_base_50_0010"""
    os.makedirs('traces', exist_ok=True)
    os.makedirs('report', exist_ok=True)

    start_time = datetime(2024, 5, 12, 14, 20, 0, 0)
    current_time = start_time

    def advance_time(ms=1):
        nonlocal current_time
        # Add slight jitter for realism
        current_time += timedelta(microseconds=ms * 1000 + random.randint(10, 100))
        return current_time.strftime("[%H:%M:%S.%f]")[:-3] + "]"

    def make_txn(addr_hex, is_read, reg_hex, data_hex_list, nack_at_data_idx=-1):
        lines = []
        lines.append(f"{advance_time()} [CH0] I2C START")
        
        # Calculate 8-bit address (7-bit << 1 | R/W)
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
                    lines.append(f"{advance_time()} [CH0] TX: NACK") # Master NACKs last read byte
                else:
                    lines.append(f"{advance_time()} [CH0] TX: ACK")
            else:
                lines.append(f"{advance_time()} [CH0] TX: {data}")
                if i == nack_at_data_idx:
                    lines.append(f"{advance_time()} [CH0] RX: NACK")
                    break # Abort txn on NACK
                else:
                    lines.append(f"{advance_time()} [CH0] RX: ACK")

        lines.append(f"{advance_time()} [CH0] I2C STOP")
        return lines

    log_lines = []

    # File Header
    log_lines.append("=== SALEAE LOGIC EXPORT V2.1.4 RAW DUMP ===")
    log_lines.append("=== PROTOCOL: I2C (FAST MODE 400KHZ) ===")
    log_lines.append(f"=== CAPTURE START: {start_time.isoformat()} ===")
    log_lines.append("ERR: High Level Analyzer Plugin 'I2C_Decoder' crashed. Dumping raw symbols.")
    log_lines.append("-" * 50)

    # Noise: EEPROM Read operations (Address 0x50 -> Write 0xA0, Read 0xA1)
    for _ in range(3):
        # Dummy write register address 0x00
        log_lines.extend(make_txn('50', False, f"{random.randint(0, 255):02X}", []))
        # Read 4 bytes
        log_lines.extend(make_txn('50', True, None, [f"{random.randint(0, 255):02X}" for _ in range(4)]))
        current_time += timedelta(milliseconds=12)

    # Noise: PMIC Configuration (Address 0x34 -> Write 0x68)
    log_lines.extend(make_txn('34', False, '10', ['FF']))
    log_lines.extend(make_txn('34', False, '11', ['80']))
    log_lines.extend(make_txn('34', False, '14', ['0F']))
    current_time += timedelta(milliseconds=45)

    log_lines.append(f"{advance_time()} --- SYS EVENT: GPIO_INT0 RISING EDGE (WAKEUP) ---")

    # Target IMU Initialization sequence (Address 0x68 -> Write 0xD0)
    log_lines.extend(make_txn('68', False, '6B', ['00'])) # Pwr mgmt 1: wake up
    log_lines.extend(make_txn('68', False, '1A', ['03'])) # Config: DLPF
    log_lines.extend(make_txn('68', False, '1B', ['18'])) # Gyro config: 2000dps
    log_lines.extend(make_txn('68', False, '1C', ['08'])) # Accel config: 4g

    # INTENTIONAL BUG INJECTION
    # Trying to write invalid data 0x7F to reserved register 0x2A.
    # The sensor responds with a NACK on the data byte.
    log_lines.extend(make_txn('68', False, '2A', ['7F'], nack_at_data_idx=0))

    current_time += timedelta(milliseconds=5)

    # Subsequent error handling noise from MCU (trying to reset bus, etc.)
    log_lines.append(f"{advance_time()} --- SYS EVENT: I2C_ERR_INTERRUPT ---")
    log_lines.extend(make_txn('50', False, '00', ['01'])) 
    log_lines.extend(make_txn('68', False, '6B', ['80'])) # Try soft reset, maybe fails too

    # Write out the raw log file
    with open('traces/bus_analyzer_export.log', 'w') as f:
        f.write('\n'.join(log_lines) + '\n')
