import os
import shutil

def create_env():
    asset_dir = "assets/data_06"
    if os.path.exists(asset_dir):
        shutil.rmtree(asset_dir)
    os.makedirs(asset_dir)

    # Manual file
    manual_content = """Notes on Data Protocol for Model D-1972

The instrument transmits data continuously. Each frame consists of 8 bytes:
[Byte 0] Sync Byte 1: 0xAA
[Byte 1] Sync Byte 2: 0x55
[Byte 2-3] Temperature: 16-bit signed integer (Big-Endian). Divide by 100.0 to get Celsius.
[Byte 4-5] Pressure: 16-bit unsigned integer (Big-Endian). Value is in hPa.
[Byte 6] Humidity: 8-bit unsigned integer. Value is in %.
[Byte 7] Checksum: The sum of Bytes 0 through 6, modulo 256 (i.e., keep the lowest 8 bits).

Note: Due to line noise, some frames may be corrupted. Always verify the checksum before recording the data.
"""
    with open(os.path.join(asset_dir, "manual.txt"), "w") as f:
        f.write(manual_content)

    # Data generation
    # Valid 1: Temp: 25.00C (0x09C4), Press: 1013 (0x03F5), Hum: 45 (0x2D)
    # Checksum: AA + 55 + 09 + C4 + 03 + F5 + 2D = 0351 -> 51
    frame1 = "AA 55 09 C4 03 F5 2D 51"

    # Valid 2: Temp: -5.50C (0xFE0A -> -502), Press: 990 (0x03DE), Hum: 60 (0x3C)
    # Checksum: AA + 55 + FE + 0A + 03 + DE + 3C = 0328 -> 28
    frame2 = "AA 55 FE 0A 03 DE 3C 28"

    # Invalid 1 (corrupted checksum): 
    # Let's say Temp: 20.00C (0x07D0), Press: 1000 (0x03E8), Hum: 50 (0x32)
    # True checksum: AA + 55 + 07 + D0 + 03 + E8 + 32 = 02ED -> ED
    # Fake checksum: 00
    frame3 = "AA 55 07 D0 03 E8 32 00"

    # Valid 3: Temp: 10.25C (0x0401), Press: 1005 (0x03ED), Hum: 55 (0x37)
    # Checksum: AA + 55 + 04 + 01 + 03 + ED + 37 = 022A -> 2A
    frame4 = "AA 55 04 01 03 ED 37 2A"

    # Write to hex file
    dump_content = f"{frame1}\n{frame2}\n{frame3}\n{frame4}\n"
    with open(os.path.join(asset_dir, "sensor_dump.hex"), "w") as f:
        f.write(dump_content)

if __name__ == "__main__":
    create_env()
