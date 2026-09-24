import os
import json
import random

def build_env():
    # Initialize directories directly in the current working directory
    os.makedirs('configs', exist_ok=True)
    os.makedirs('engineering/hardware/errata', exist_ok=True)
    os.makedirs('debug', exist_ok=True)
    os.makedirs('system_logs/bus_traces', exist_ok=True)
    
    # 1. Forge the Deployment Map (Fragmented config layer)
    devices = {}
    for i in range(1, 1500):
        devices[f"GTW-Alpha-{i:04d}"] = f"SN-1{i:03d}-REV_A"
        devices[f"GTW-Beta-{i:04d}"]  = f"SN-2{i:03d}-REV_C"
    
    # The true target hidden in the haystack
    devices["GTW-Omega-99"] = "SN-8832-REV_K"
    
    # More noise
    for i in range(1, 800):
        devices[f"GTW-Zeta-{i:04d}"]  = f"SN-9{i:03d}-REV_X"
        
    with open('configs/deployment_map.json', 'w', encoding='utf-8') as f:
        json.dump(devices, f, indent=2)
        
    # 2. Forge the Hardware Errata docs (Decoys and True clues)
    errata_a = """# SILICON ERRATA - REV A
**Component**: EEPROM (I2C Addr `0x50`)
**Issue**: Burst read exceeding 16 bytes causes internal buffer overflow. May result in `[BROWNOUT_RESET]`.
"""
    with open('engineering/hardware/errata/REV_A.md', 'w', encoding='utf-8') as f: f.write(errata_a)
    
    errata_c = """# SILICON ERRATA - REV C
**Component**: SPI Flash Memory
**Issue**: Continuous polling of the status register leaks internal state. Watch out for `[SW_WDOG_BITE]` in system logs due to high CPU blocking wait.
"""
    with open('engineering/hardware/errata/REV_C.md', 'w', encoding='utf-8') as f: f.write(errata_c)
    
    errata_x = """# SILICON ERRATA - REV X
**Component**: IMU Sensor (I2C Addr `0x68`)
**Issue**: Writing `0xFF` to Reg `0x19` deadlocks the sensor.
"""
    with open('engineering/hardware/errata/REV_X.md', 'w', encoding='utf-8') as f: f.write(errata_x)

    errata_k = """# SILICON ERRATA - REV K

**Severity**: CRITICAL
**Component**: System PMIC (7-bit I2C Address `0x5C`)

**Description**: 
On Rev K boards, the power management IC has a severe undocumented state machine bug. 
If ANY value is written to the `LDO_CFG` register (Offset `0x3A`) where BOTH Bit 3 and Bit 6 are asserted high simultaneously (i.e., `(val & 0x48) == 0x48`), the I2C physical layer immediately deadlocks. The SCL line gets permanently pulled low by the PMIC. 

Because the PMIC stops serving the CPU core voltage regulator properly during this SCL deadlock, the core stalls, ultimately triggering a fatal hardware watchdog reset signature: `[HW_WDOG_BITE]`.

**Workaround**:
Ensure standard operating values (typically `0x00` to `0x07`) are exclusively used. Do NOT let any software component set bit 3 and 6 simultaneously.
"""
    with open('engineering/hardware/errata/REV_K.md', 'w', encoding='utf-8') as f: f.write(errata_k)

    # 3. Forge Massive Log Fragments
    # We will generate 5 days * 12 hours of logs = 60 directories/files, hundreds of thousands of lines
    random.seed(42) # Ensure deterministic noise generation
    for day in range(10, 15):
        dir_path = f'system_logs/bus_traces/2024-11-{day:02d}'
        os.makedirs(dir_path, exist_ok=True)
        for hour in range(0, 24, 2):
            log_name = f"{dir_path}/capture_{hour:02d}00.log"
            with open(log_name, 'w', encoding='utf-8') as f:
                f.write("=== LOGIC ANALYZER DUMP : RAW EVENT STREAM ===\n")
                # Generate tons of normal traffic
                for _ in range(300):
                    # Normal Write to 0x5C (PMIC), safe value 0x01
                    f.write(f"[{hour:02d}:15:00.123] EVENT: I2C_START\n")
                    f.write(f"[{hour:02d}:15:00.124] EVENT: I2C_WR | DATA: 0xB8 | STATUS: ACK\n") # 0x5C << 1
                    f.write(f"[{hour:02d}:15:00.125] EVENT: I2C_DAT | DATA: 0x3A | STATUS: ACK\n")
                    f.write(f"[{hour:02d}:15:00.126] EVENT: I2C_DAT | DATA: 0x01 | STATUS: ACK\n")
                    
                    # Decoy traffic to other sensors
                    f.write(f"[{hour:02d}:18:22.441] EVENT: I2C_START\n")
                    f.write(f"[{hour:02d}:18:22.442] EVENT: I2C_WR | DATA: 0xD0 | STATUS: ACK\n") # 0x68 << 1
                    f.write(f"[{hour:02d}:18:22.443] EVENT: I2C_DAT | DATA: 0x19 | STATUS: ACK\n")
                    f.write(f"[{hour:02d}:18:22.444] EVENT: I2C_DAT | DATA: 0x00 | STATUS: ACK\n")

                # Inject fake software watchdog bite (noise)
                if random.random() > 0.5:
                    f.write(f"[{hour:02d}:59:59.000] SYSTEM WARNING: KERNEL TASK BLOCKED > 120s\n")
                    f.write(f"[{hour:02d}:59:59.999] [SW_WDOG_BITE] SYSTEM RESET INITIATED\n")

    # 4. Inject the True Fatal Sequence into one specific file
    true_log = 'system_logs/bus_traces/2024-11-14/capture_1400.log'
    with open(true_log, 'a', encoding='utf-8') as f:
        f.write("\n=== ANOMALY SEQUENCE DETECTED ===\n")
        f.write("[14:23:45.101] EVENT: I2C_START\n")
        f.write("[14:23:45.102] EVENT: I2C_WR | DATA: 0xB8 | STATUS: ACK\n") # 0x5C << 1
        f.write("[14:23:45.103] EVENT: I2C_DAT | DATA: 0x3A | STATUS: ACK\n")
        f.write("[14:23:45.104] EVENT: I2C_DAT | DATA: 0x4F | STATUS: NAK\n") # 0x4F triggers the Bit 3 + 6 mask (0x48)
        f.write("[14:23:45.105] ALARM: BUS_LOCKED_SCL_LOW - TIMEOUT DETECTED\n")
        f.write("[14:23:46.000] SYSTEM WARNING: PMIC_VCORE_UNSTABLE\n")
        f.write("[14:23:47.000] [HW_WDOG_BITE] SYSTEM HALT - HARDWARE WATCHDOG RESET TRIGGERED!!\n")
        f.write("=== STREAM EOF ===\n")

if __name__ == "__main__":
    build_env()
