import os
import random

def generate_noise_spi():
    """Generate some dummy SPI flash read traffic"""
    addr = random.randint(0x000000, 0x0FFFFF)
    data = [f"{random.randint(0, 255):02X}" for _ in range(8)]
    return f"SPI CS LOW | CMD: 03 | ADDR: {addr:06X} | MISO: {' '.join(data)} | CS HIGH\n"

def generate_normal_i2c():
    """Generate normal I2C traffic for the IMU sensor (Addr 0x68)"""
    # 0xD0 is 0x68 << 1 + 0 (Write)
    regs = [0x19, 0x1A, 0x1B, 0x1C, 0x23, 0x24]
    reg = random.choice(regs)
    val = random.randint(0x00, 0x0F)
    return (
        f"I2C START\n"
        f"I2C TX: D0 [ACK]\n"
        f"I2C TX: {reg:02X} [ACK]\n"
        f"I2C TX: {val:02X} [ACK]\n"
        f"I2C STOP\n"
    )

def build_env():
    # Create necessary directories directly in the current working directory (assets/data_persona_aligned_base_50_0021/)
    os.makedirs('traces', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('debug', exist_ok=True)
    os.makedirs('firmware', exist_ok=True)

    # 1. Create a messy hardware notes file (datasheet excerpt)
    hw_notes = """
>> FORWARDED MESSAGE FROM FAE (DO NOT DISTRIBUTE) <<
Subject: RE: Rev B Silicon Errata - MPU variant

Hey man,
Sorry about the boot loops you're seeing. Yeah, the new batch of ASICs (I2C Base Addr: 0x68, assuming AD0 tied to GND) has a critical silicon bug in the power management block. 

Register map quick ref:
Reg 0x19 (25) : SMPLRT_DIV
Reg 0x1A (26) : CONFIG
Reg 0x1B (27) : GYRO_CONFIG
Reg 0x1C (28) : ACCEL_CONFIG
...
Reg 0x6B (107): PWR_MGMT_1

WARNING: 
Normal operational values for PWR_MGMT_1 are 0x00 (awake) to 0x09. 
DO NOT write bit 7 (value 0x80) to Register 0x6B (PWR_MGMT_1) under ANY circumstances on Rev B! 
Setting the DEVICE_RESET bit high alongside the sleep bit triggers a physical clock stretch lockup (SCL held low infinitely). Watchdog will definitely bite if this happens.

Other sensors on bus:
0x3C (OLED Display)
0x50 (EEPROM)

Let me know if patching the driver works.
"""
    with open("docs/hw_notes.txt", "w", encoding="utf-8") as f:
        f.write(hw_notes.strip())

    # 2. Create the unstructured logic analyzer dump
    bus_log_path = "traces/bus_capture.log"
    with open(bus_log_path, "w", encoding="utf-8") as f:
        f.write("LOGIC ANALYZER EXPORT - CH0: SCL, CH1: SDA, CH2: SPI_CLK, CH3: SPI_MISO, CH4: SPI_MOSI, CH5: SPI_CS\n")
        f.write("TIMESTAMP FORMAT: [SS.MMMMMM]\n")
        f.write("="*80 + "\n")
        
        timestamp = 0.012000
        
        # Write some normal traffic
        for _ in range(45):
            if random.random() > 0.4:
                f.write(f"[{timestamp:.6f}] {generate_noise_spi()}")
                timestamp += random.uniform(0.0001, 0.005)
            else:
                lines = generate_normal_i2c().split('\n')
                for line in lines:
                    if line.strip():
                        f.write(f"[{timestamp:.6f}] {line}\n")
                        timestamp += 0.00005
                timestamp += random.uniform(0.001, 0.01)

        # Write the fatal traffic that causes the crash
        f.write(f"[{timestamp:.6f}] SPI CS LOW | CMD: 0B | ADDR: 01F400 | MISO: 00 FF FF FF | CS HIGH\n")
        timestamp += 0.0015
        f.write(f"[{timestamp:.6f}] I2C START\n")
        timestamp += 0.0001
        f.write(f"[{timestamp:.6f}] I2C TX: D0 [ACK]\n") # 0x68 << 1 + 0 (Write)
        timestamp += 0.0001
        f.write(f"[{timestamp:.6f}] I2C TX: 6B [ACK]\n") # Reg 0x6B (PWR_MGMT_1)
        timestamp += 0.0001
        f.write(f"[{timestamp:.6f}] I2C TX: 80 [NAK]\n") # Bad Value 0x80
        timestamp += 0.0001
        f.write(f"[{timestamp:.6f}] I2C SCL HELD LOW (CLOCK STRETCH DETECTED - TIMEOUT EXCEEDED)\n")
        timestamp += 0.05
        f.write(f"[{timestamp:.6f}] SYSTEM WARNING: I2C BUS DEADLOCK\n")
        timestamp += 2.0
        f.write(f"[{timestamp:.6f}] MCU KERNEL PANIC: HARDWARE WATCHDOG RESET TRIGGERED!!!\n")
        f.write("="*80 + "\n")
        f.write("CAPTURE TERMINATED UNEXPECTEDLY.\n")

    # 3. Create a decoy binary file
    with open("firmware/bootloader_dump.hex", "w", encoding="utf-8") as f:
        for i in range(20):
            addr = i * 16
            data = "".join([f"{random.randint(0, 255):02X}" for _ in range(16)])
            checksum = f"{random.randint(0, 255):02X}"
            f.write(f":10{addr:04X}00{data}{checksum}\n")
        f.write(":00000001FF\n")

if __name__ == "__main__":
    build_env()
