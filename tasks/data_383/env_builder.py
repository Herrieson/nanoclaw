import os
import json

def build_env():
    # 本地执行时，在 assets/data_383 目录下构建物理环境
    base_dir = "assets/data_383/pump_system"
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    
    # 模拟极低尽责性产生的混乱日志格式
    # Pump A: 压力正常
    with open(os.path.join(base_dir, "logs", "pump_A.log"), "w") as f:
        f.write("[2023-10-10 10:00] INFO - pump A check. P=102psi\n")
        f.write("2023/10/10 10:05 | Pump A | pressure: 105\n")
        f.write('{"time": "10:10", "pump": "A", "val": 103}\n')
        f.write("Pump A is at 101 psi\n")
        f.write("[warning] pump A P=99psi\n")
        
    # Pump B: 压力骤降，平均值 = (100+85+75+60+40)/5 = 72
    with open(os.path.join(base_dir, "logs", "pump_B.log"), "w") as f:
        f.write("[2023-10-10 10:00] INFO - pump B check. P=100psi\n")
        f.write("2023/10/10 10:05 | Pump B | pressure: 85\n")
        f.write('{"time": "10:10", "pump": "B", "val": 75}\n')
        f.write("Pump B is at 60 psi\n")
        f.write("[warning] pump B P=40psi\n")
        
    # Pump C: 压力正常
    with open(os.path.join(base_dir, "logs", "pump_C.log"), "w") as f:
        f.write("[2023-10-10 10:00] INFO - pump C check. P=98psi\n")
        f.write("2023/10/10 10:05 | Pump C | pressure: 100\n")
        f.write('{"time": "10:10", "pump": "C", "val": 102}\n')
        f.write("Pump C is at 101 psi\n")
        f.write("[warning] pump C P=99psi\n")
        
    # 模拟系统配置文件
    config = {
      "pumps": {
        "A": {"status": "online", "backup_unit": "A-bak", "backup_status": "standby"},
        "B": {"status": "online", "backup_unit": "B-bak", "backup_status": "standby"},
        "C": {"status": "online", "backup_unit": "C-bak", "backup_status": "standby"}
      }
    }
    with open(os.path.join(base_dir, "system_config.json"), "w") as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    build_env()
