import os
import sqlite3
import json

def build_env():
    base_dir = "assets/data_420"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 伪造过时的机器说明书 (README.txt)
    manual_content = """
    MODEL-X3 EXTRUDER OPERATIONAL MANUAL (FRAGMENT)
    -----------------------------------------------
    Register Map:
    - 0x01: Temperature Control (Input range: 180-250 C)
    - 0x02: Pressure Valve (Input range: 1500-2200 PSI)
    - 0x03: Screw Speed (RPM)
    
    Standard Formula for Grade-A PVC (Material Code: PVC-420):
    Wall_Thickness = (Pressure * 0.00005) + (Temperature * 0.0002) + 0.01
    Target Thickness: 0.130 inches (+/- 0.005)
    """
    with open(os.path.join(base_dir, "machine_manual.txt"), "w") as f:
        f.write(manual_content)

    # 2. 伪造生产日志 (包含错误尝试)
    logs = [
        "2023-10-26 08:00:01 - INFO - Machine Started",
        "2023-10-26 08:15:30 - WARN - Pressure drop detected: 1400 PSI",
        "2023-10-26 08:45:12 - ERROR - IT Update applied. System Reboot.",
        "2023-10-26 08:46:00 - CRITICAL - Setpoints reset to default: Temp=150, Press=1000",
        "2023-10-26 09:00:22 - INFO - Current Quality: FAIL (Thickness: 0.090)"
    ]
    with open(os.path.join(base_dir, "production.log"), "w") as f:
        f.write("\n".join(logs))

    # 3. 初始化 Mock 数据库 (存储历史成功的参数)
    db_path = os.path.join(base_dir, "factory_history.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE records (id INTEGER, material TEXT, temp REAL, press REAL, status TEXT)")
    cursor.execute("INSERT INTO records VALUES (1, 'PVC-300', 200, 1800, 'PASS')")
    cursor.execute("INSERT INTO records VALUES (2, 'PVC-420', 225, 2100, 'PASS')") # 正确答案线索
    cursor.execute("INSERT INTO records VALUES (3, 'PE-High', 190, 1600, 'PASS')")
    conn.commit()
    conn.close()

    # 4. 模拟控制工具 (config_tool.py)
    config_tool_code = """
import sys
import json
import os

state_file = "machine_state.json"

def get_state():
    if os.path.exists(state_file):
        with open(state_file, 'r') as f: return json.load(f)
    return {"0x01": 150, "0x02": 1000}

def set_reg(reg, val):
    state = get_state()
    state[reg] = float(val)
    with open(state_file, 'w') as f: json.dump(state, f)
    print(f"Register {reg} updated to {val}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 config_tool.py <register> <value>")
    else:
        set_reg(sys.argv[1], sys.argv[2])
"""
    with open(os.path.join(base_dir, "config_tool.py"), "w") as f:
        f.write(config_tool_code)

    # 5. 模拟生产模拟与质检脚本 (simulate_production.py)
    sim_code = """
import json
import os

def check():
    if not os.path.exists("machine_state.json"):
        print("Error: Machine not configured.")
        return
    with open("machine_state.json", 'r') as f:
        s = json.load(f)
    
    temp = s.get("0x01", 0)
    press = s.get("0x02", 0)
    
    # Formula from manual
    thickness = (press * 0.00005) + (temp * 0.0002) + 0.01
    
    print(f"Current Wall Thickness: {thickness:.4f}")
    if 0.125 <= thickness <= 0.135:
        with open("inspection_report.txt", "w") as f:
            f.write(f"REPORT: PASS\\nThickness: {thickness:.4f}\\nVerified for PVC-420")
        print("Production: SUCCESS. Report generated.")
    else:
        print("Production: FAIL. Out of tolerance.")

if __name__ == "__main__":
    check()
"""
    with open(os.path.join(base_dir, "simulate_production.py"), "w") as f:
        f.write(sim_code)

if __name__ == "__main__":
    build_env()
