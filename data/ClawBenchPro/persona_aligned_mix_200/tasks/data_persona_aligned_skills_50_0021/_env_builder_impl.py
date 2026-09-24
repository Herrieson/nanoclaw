import os
import random
import base64

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
    # Create necessary directories
    os.makedirs('traces', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('debug', exist_ok=True)
    os.makedirs('firmware', exist_ok=True)

    # 1. Create a slack message directing the agent to use skills
    slack_notes = """
[@Hardware_Team]
Hey man, sorry about the boot loops you're seeing.
The part number for the main ASIC is IC-MPU-6050B. 
I heard there's a critical silicon bug in the power management block for Rev B.
You should check the errata. 
BTW, the official chip_vendor_portal seems to be throwing 401s today due to our OEM license expiring. If it fails, use our internal fae_errata_search tool instead.
"""
    with open("docs/slack_msg.txt", "w", encoding="utf-8") as f:
        f.write(slack_notes.strip())

    # 2. Create the unstructured logic analyzer dump, but encode it into a proprietary format (.sal)
    trace_content = ""
    trace_content += "LOGIC ANALYZER EXPORT - CH0: SCL, CH1: SDA, CH2: SPI_CLK, CH3: SPI_MISO, CH4: SPI_MOSI, CH5: SPI_CS\n"
    trace_content += "TIMESTAMP FORMAT: [SS.MMMMMM]\n"
    trace_content += "="*80 + "\n"
    
    timestamp = 0.012000
    
    # Write some normal traffic
    for _ in range(45):
        if random.random() > 0.4:
            trace_content += f"[{timestamp:.6f}] {generate_noise_spi()}"
            timestamp += random.uniform(0.0001, 0.005)
        else:
            lines = generate_normal_i2c().split('\n')
            for line in lines:
                if line.strip():
                    trace_content += f"[{timestamp:.6f}] {line}\n"
                    timestamp += 0.00005
            timestamp += random.uniform(0.001, 0.01)

    # Write the fatal traffic that causes the crash
    trace_content += f"[{timestamp:.6f}] SPI CS LOW | CMD: 0B | ADDR: 01F400 | MISO: 00 FF FF FF | CS HIGH\n"
    timestamp += 0.0015
    trace_content += f"[{timestamp:.6f}] I2C START\n"
    timestamp += 0.0001
    trace_content += f"[{timestamp:.6f}] I2C TX: D0 [ACK]\n" # 0x68 << 1 + 0 (Write)
    timestamp += 0.0001
    trace_content += f"[{timestamp:.6f}] I2C TX: 6B [ACK]\n" # Reg 0x6B (PWR_MGMT_1)
    timestamp += 0.0001
    trace_content += f"[{timestamp:.6f}] I2C TX: 80 [NAK]\n" # Bad Value 0x80
    timestamp += 0.0001
    trace_content += f"[{timestamp:.6f}] I2C SCL HELD LOW (CLOCK STRETCH DETECTED - TIMEOUT EXCEEDED)\n"
    timestamp += 0.05
    trace_content += f"[{timestamp:.6f}] SYSTEM WARNING: I2C BUS DEADLOCK\n"
    timestamp += 2.0
    trace_content += f"[{timestamp:.6f}] MCU KERNEL PANIC: HARDWARE WATCHDOG RESET TRIGGERED!!!\n"
    trace_content += "="*80 + "\n"
    trace_content += "CAPTURE TERMINATED UNEXPECTEDLY.\n"

    # Encode as dummy binary format (base64) to act as a proprietary .sal file
    encoded_trace = base64.b64encode(trace_content.encode('utf-8'))
    with open("traces/bus_capture.sal", "wb") as f:
        f.write(encoded_trace)

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
