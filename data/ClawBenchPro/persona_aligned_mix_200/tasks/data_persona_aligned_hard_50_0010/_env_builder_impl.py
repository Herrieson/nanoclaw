import os
import random
import string
from datetime import datetime, timedelta

def build_env():
    """Builds the deep-abyss environment for data_persona_aligned_hard_50_0010"""
    os.makedirs('traces', exist_ok=True)
    os.makedirs('report', exist_ok=True)
    os.makedirs('firmware/board/headers', exist_ok=True)
    os.makedirs('logs/sys', exist_ok=True)

    # 1. Provide Firmware Header File (Decoy + True Base Address)
    header_content = """
#ifndef BOARD_DEVICES_H
#define BOARD_DEVICES_H

// Core PMIC Controller
#define PMIC_BASE_ADDR 0x34

// EEPROM Memory
#define EEPROM_BASE_ADDR 0x50

// Nova-IMU-6DoF Sensor (Rev B)
// BASE 7-bit Address is 0x68.
// The actual address depends on the HW_STRAP_PIN_1 state.
// If HW_STRAP_PIN_1 is LOW (0), addr = 0x68
// If HW_STRAP_PIN_1 is HIGH (1), addr = 0x69
#define NOVA_IMU_BASE_ADDR 0x68

#endif // BOARD_DEVICES_H
"""
    with open('firmware/board/headers/devices.h', 'w') as f:
        f.write(header_content.strip() + '\n')

    # 2. Provide Boot Log to determine true address
    boot_log = """
[0.000] SYS: Booting Rev B core board...
[0.005] SYS: Initializing GPIO subsystem...
[0.012] SYS: Reading hardware strap pins for I2C conflict resolution...
[0.015] SYS: HW_STRAP_PIN_1 state: HIGH (1)  -> Address offset +1 applied.
[0.016] SYS: HW_STRAP_PIN_2 state: LOW (0)
[0.020] SYS: Bringing up I2C0 bus...
[0.025] SYS: Handing over control to kernel drivers.
"""
    with open('logs/sys/hw_bootstrap.log', 'w') as f:
        f.write(boot_log.strip() + '\n')

    # 3. Generate massive fragmented trace logs
    start_time = datetime(2024, 11, 23, 8, 0, 0, 0)
    current_time = start_time

    def advance_time(ms_min=0, ms_max=2):
        nonlocal current_time
        current_time += timedelta(microseconds=random.randint(ms_min*1000, ms_max*1000 + 500))
        return current_time.strftime("[%H:%M:%S.%f]")[:-3] + "]"

    def make_i2c_txn(addr_7bit_hex, is_read, reg_hex, data_hex_list, error_type="NONE"):
        """
        error_type:
        "NONE" -> successful transaction
        "DATA_NACK" -> slave NACKs on writing a specific data byte
        "REG_NACK" -> slave NACKs on register address
        """
        lines = []
        lines.append(f"{advance_time()} CH0: START")
        
        # Calculate 8-bit address
        addr_byte = (int(addr_7bit_hex, 16) << 1) | (1 if is_read else 0)
        lines.append(f"{advance_time()} CH0: M->S TX: {addr_byte:02X}")
        lines.append(f"{advance_time()} CH0: S->M RX: ACK")

        # Register phase
        if reg_hex is not None:
            lines.append(f"{advance_time()} CH0: M->S TX: {reg_hex}")
            if error_type == "REG_NACK":
                lines.append(f"{advance_time()} CH0: S->M RX: NACK")
                lines.append(f"{advance_time()} CH0: STOP")
                return lines
            else:
                lines.append(f"{advance_time()} CH0: S->M RX: ACK")

        # Data phase
        for i, data in enumerate(data_hex_list):
            if is_read:
                lines.append(f"{advance_time()} CH0: S->M RX: {data}")
                if i == len(data_hex_list) - 1:
                    # Master NACKs last read byte to signal stop (Normal behavior!)
                    lines.append(f"{advance_time()} CH0: M->S TX: NACK") 
                else:
                    lines.append(f"{advance_time()} CH0: M->S TX: ACK")
            else:
                lines.append(f"{advance_time()} CH0: M->S TX: {data}")
                if error_type == "DATA_NACK" and i == len(data_hex_list) - 1:
                    # Slave NACKs the written data byte (This is a fault!)
                    lines.append(f"{advance_time()} CH0: S->M RX: NACK")
                    break
                else:
                    lines.append(f"{advance_time()} CH0: S->M RX: ACK")

        lines.append(f"{advance_time()} CH0: STOP")
        return lines

    # Pre-generate noise transactions
    all_txns = []

    # Noise 1: EEPROM Read/Writes
    for _ in range(800):
        # Write register
        all_txns.append(make_i2c_txn('50', False, f"{random.randint(0, 255):02X}", []))
        # Read seq
        all_txns.append(make_i2c_txn('50', True, None, [f"{random.randint(0, 255):02X}" for _ in range(random.randint(1, 8))]))

    # Noise 2: PMIC Configuration (Address 0x34)
    # DECOY WARNING: 0x34 << 1 = 0x68! A write to PMIC shows up as TX: 68!
    # If the Agent just greps for "68" they will find these PMIC logs and get completely confused!
    for _ in range(400):
        all_txns.append(make_i2c_txn('34', False, f"{random.randint(0, 127):02X}", [f"{random.randint(0, 255):02X}"]))
        all_txns.append(make_i2c_txn('34', True, None, [f"{random.randint(0, 255):02X}"]))

    # Noise 3: Random other unknown devices
    for _ in range(300):
        all_txns.append(make_i2c_txn('2A', False, '01', ['0F']))

    # Target: Nova-IMU sequence (Address depends on strap, base 0x68, pin is HIGH, so 0x69)
    # 0x69 Write is D2.
    target_txns = []
    target_txns.append(make_i2c_txn('69', False, '6B', ['00'])) # Wake up
    target_txns.append(make_i2c_txn('69', False, '1A', ['03'])) # Config
    target_txns.append(make_i2c_txn('69', False, '1B', ['18'])) # Gyro
    
    # THE FATAL BUG INJECTION!
    # Master tries to write value 0xFA to register 0x4C, slave NACKs it!
    target_txns.append(make_i2c_txn('69', False, '4C', ['FA'], error_type="DATA_NACK"))

    # Mix target_txns into the massive pool at a random but contiguous location
    insertion_idx = random.randint(100, len(all_txns) - 10)
    all_txns[insertion_idx:insertion_idx] = target_txns

    # Write out to 250 fragmented files in 10 different directories
    num_dirs = 10
    files_per_dir = 25
    lines_per_file = []
    
    current_lines_acc = []
    for txn in all_txns:
        current_lines_acc.extend(txn)

    # Chunk the massive lines into files
    chunk_size = len(current_lines_acc) // (num_dirs * files_per_dir) + 1
    
    line_idx = 0
    for d_idx in range(num_dirs):
        dir_path = f"traces/session_{d_idx:02d}"
        os.makedirs(dir_path, exist_ok=True)
        for f_idx in range(files_per_dir):
            file_path = os.path.join(dir_path, f"part_{f_idx:03d}.log")
            with open(file_path, 'w') as f:
                f.write("=== LOG FRAGMENT START ===\n")
                chunk = current_lines_acc[line_idx:line_idx+chunk_size]
                f.write('\n'.join(chunk) + '\n')
                line_idx += chunk_size
