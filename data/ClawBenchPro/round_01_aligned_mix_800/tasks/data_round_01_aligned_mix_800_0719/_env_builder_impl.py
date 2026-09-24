import os
import json

def build_env():
    # Create directories
    os.makedirs("workspace/messy_exports", exist_ok=True)
    os.makedirs("workspace/for_boss", exist_ok=True)

    # Machine A (Normal)
    with open("workspace/messy_exports/machine_A_diag.csv", "w", encoding="utf-8") as f:
        f.write("machine_id,wear_status,failed_part,uptime_hours\n")
        f.write("MACH-001,NORMAL,None,4500\n")

    # Machine B (Critical)
    with open("workspace/messy_exports/machine_B_diag.csv", "w", encoding="utf-8") as f:
        f.write("machine_id,wear_status,failed_part,uptime_hours\n")
        f.write("MACH-002,CRITICAL,Spindle_Assembly,8200\n")

    # Machine C (Critical)
    with open("workspace/messy_exports/machine_C_diag.csv", "w", encoding="utf-8") as f:
        f.write("machine_id,wear_status,failed_part,uptime_hours\n")
        f.write("MACH-003,CRITICAL,Servo_Motor,9100\n")

    # Machine D (Warning - not critical)
    with open("workspace/messy_exports/machine_D_diag.csv", "w", encoding="utf-8") as f:
        f.write("machine_id,wear_status,failed_part,uptime_hours\n")
        f.write("MACH-004,WARNING,Coolant_Pump,6000\n")

    # Price list
    prices = {
        "Spindle_Assembly": 850.00,
        "Servo_Motor": 1200.00,
        "Coolant_Pump": 300.00,
        "Cutting_Tool": 45.00
    }
    with open("workspace/messy_exports/part_prices.json", "w", encoding="utf-8") as f:
        json.dump(prices, f, indent=2)

    # Distraction 1: Gardening
    with open("workspace/messy_exports/weekend_garden_notes.txt", "w", encoding="utf-8") as f:
        f.write("Need to buy seeds for the garden this weekend:\n")
        f.write("- Cải bẹ xanh (Mustard greens)\n")
        f.write("- Rau muống (Water spinach)\n")
        f.write("- Tomatoes\n")
        f.write("Make sure to water the orchids!\n")

    # Distraction 2: Music Playlist
    with open("workspace/messy_exports/cai_luong_playlist.txt", "w", encoding="utf-8") as f:
        f.write("My favorite relaxing tracks:\n")
        f.write("1. Dạ Cổ Hoài Lang\n")
        f.write("2. Lan Và Điệp\n")
        f.write("3. Lương Sơn Bá Chúc Anh Đài\n")

if __name__ == "__main__":
    build_env()
