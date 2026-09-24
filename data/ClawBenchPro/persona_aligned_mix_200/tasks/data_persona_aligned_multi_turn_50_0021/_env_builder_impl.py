import os
import argparse
import random

def build_turn_1():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Datasheet creation
    datasheet_content = """
# BME900 Sensor Datasheet (Draft v0.9)
I2C Device Address: 0x76 (8-bit Write: 0xEC, 8-bit Read: 0xED)

## Registers Map:
- **0x20 [PWR_CTRL]**: Power control register. 
  - 0x00: SLEEP mode (default)
  - 0x01: NORMAL mode
- **0x21 [SENSOR_CFG]**: Sensor configuration. 
  - 0x00: Disabled (default)
  - 0x0F: High-Resolution Active
- **0x30 [WATCHDOG]**: Watchdog control.
  - 0x01: Arm watchdog
  - 0xAA: Pet watchdog (reset timer)

## WARNINGS & CONSTRAINTS (CRITICAL)
- **Constraint A**: Writing to [SENSOR_CFG] (0x21) while [PWR_CTRL] (0x20) is currently in NORMAL mode (0x01) will cause an immense current spike and trigger a BROWNOUT WARNING. Always configure [SENSOR_CFG] ONLY when the device is in SLEEP mode.
- **Note**: The I2C bus clock operates at 400kHz.
"""
    with open("docs/datasheet_BME900.md", "w") as f:
        f.write(datasheet_content)
        
    # Logic Analyzer Dump creation (Messy, mixed with SPI noise)
    dump_lines = []
    base_time = 12.0000
    
    def add_i2c(t, reg, val):
        dump_lines.append(f"[{t:.4f}] I2C START | ADDR: 0xEC (W) | ACK | REG: {reg} | ACK | DATA: {val} | ACK | I2C STOP")
    
    def add_spi_noise(t):
        dump_lines.append(f"[{t:.4f}] SPI_CS_LOW | MOSI: 0x{random.randint(0, 255):02X} | MISO: 0x00 | SPI_CS_HIGH")

    # Sequence generation
    current_time = base_time
    for _ in range(5):
        add_spi_noise(current_time)
        current_time += 0.005
        
    add_i2c(current_time, "0x30", "0x01") # Arm Watchdog
    current_time += 0.015
    add_i2c(current_time, "0x30", "0xAA") # Pet Watchdog
    current_time += 0.020
    add_i2c(current_time, "0x20", "0x01") # Set PWR_CTRL to NORMAL
    current_time += 0.010
    add_spi_noise(current_time)
    current_time += 0.005
    # VIOLATION HERE: Writing SENSOR_CFG while in NORMAL mode
    add_i2c(current_time, "0x21", "0x0F") 
    current_time += 0.015
    add_i2c(current_time, "0x30", "0xAA") # Pet Watchdog

    for _ in range(10):
        add_spi_noise(current_time)
        current_time += 0.003
        
    with open("logs/logic_analyzer_20231024.txt", "w") as f:
        f.write("\n".join(dump_lines))


def build_turn_2():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # Errata injection
    errata_content = """
# Hardware Errata for RevB (Confidential)
We fixed the I2C clock stretch issue, but discovered a new fatal flaw in the silicon logic:

## FATAL REBOOT ISSUE (Constraint B)
If the Watchdog is ARMED (0x30 == 0x01), and the Sensor is currently ACTIVE (0x21 == 0x0F), transitioning the Power Control [PWR_CTRL] (0x20) from NORMAL (0x01) back to SLEEP (0x00) creates a deadlock in the internal state machine resulting in an immediate HARD REBOOT.
Workaround: You must disable the sensor (0x21 = 0x00) BEFORE setting PWR_CTRL to SLEEP if the watchdog is running.
"""
    with open("docs/errata_revB.txt", "w") as f:
        f.write(errata_content)
        
    # Reboot Dump creation
    dump_lines = []
    base_time = 45.1000
    
    def add_i2c(t, reg, val):
        dump_lines.append(f"[{t:.4f}] I2C START | ADDR: 0xEC (W) | ACK | REG: {reg} | ACK | DATA: {val} | ACK | I2C STOP")

    current_time = base_time
    
    # Initial state setup (Valid so far based on Turn 1 & Turn 2 rules)
    add_i2c(current_time, "0x30", "0x01") # Arm Watchdog
    current_time += 0.010
    add_i2c(current_time, "0x20", "0x00") # Ensure SLEEP
    current_time += 0.010
    add_i2c(current_time, "0x21", "0x0F") # Config Sensor (Safe, because in SLEEP)
    current_time += 0.020
    add_i2c(current_time, "0x20", "0x01") # Wake up to NORMAL
    current_time += 0.015
    add_i2c(current_time, "0x30", "0xAA") # Pet Watchdog
    current_time += 0.050
    
    # Interleaved noise
    dump_lines.append(f"[{current_time:.4f}] UNKNOWN_UART_TX | MSG: 'DATA_SYNC_OK'")
    current_time += 0.010
    
    # VIOLATION HERE: Watchdog is armed, Sensor is active, changing PWR to SLEEP directly
    add_i2c(current_time, "0x20", "0x00") 
    current_time += 0.002
    dump_lines.append(f"[{current_time:.4f}] DEVICE_RESET_DETECTED | SIGNAL_LOW")
    dump_lines.append(f"[{current_time + 0.01:.4f}] BOOTROM_START | VER 1.2")

    with open("logs/field_reboot_dump.txt", "w") as f:
        f.write("\n".join(dump_lines))


def build_turn_3():
    os.makedirs("requests", exist_ok=True)
    
    request_content = """
Subject: URGENT: Driver Init Sequence Needed

We need a fresh initialization sequence for the BME900 sensor to put in our C driver. 
Please provide the sequence as a JSON array.

The sequence MUST accomplish the following final state:
1. The Watchdog MUST be ARMED.
2. The Sensor MUST be configured to High-Resolution Active (0x0F).
3. The Power Control MUST be left in NORMAL mode so we can read data.
4. You must PET the watchdog exactly once at the very end of your sequence to verify I2C stability.

You need to figure out the correct order to do this without triggering the Brownout warning from yesterday, nor the Hard Reboot from today. Start your JSON offsets at 10ms, spacing each command by 10ms.
"""
    with open("requests/patch_request.txt", "w") as f:
        f.write(request_content)


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
