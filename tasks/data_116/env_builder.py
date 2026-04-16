import os
import shutil

def build():
    base_dir = "assets/data_116"
    logs_dir = os.path.join(base_dir, "raw_logs")
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
        
    os.makedirs(logs_dir)
    
    log_1 = """
[SYS] WARN Kernel sync failed at 0x00A1
[ANIMAL] Name: Kuma   | Diet: Salmon  | Amount: 5kg   | Time: 09:00
[SYS] ERROR Memory overflow
[ARTIFACT] ID: EDO-001 | Temp: 20C | Humidity: 45% 
[ANIMAL] Name: Hachi | Diet: Bamboo Shoots | Amount: 2.5kg | Time: 08:30
[SYS] INFO Rebooting daemon...
[ARTIFACT] ID: KAMA-404| Temp: 22C | Humidity:  50%
"""

    log_2 = """
[ANIMAL] Name: Sakura | Diet: Fresh Berries | Amount:  1.2kg | Time: 10:00
[SYS] DEBUG Network unreachable
[ARTIFACT] ID: HEI-992 | Temp: 18C   | Humidity: 40%
[SYS] CRITICAL Disk drive failure on /dev/sdb
[ANIMAL] Name: Taro | Diet: Insects & Veggies | Amount: 0.5kg | Time: 11:15
[ARTIFACT] ID: ASUKA-01 | Temp:  21C | Humidity: 55%
"""

    log_3 = """
@@@GARBAGE DATA@@@
[SYS] INFO Restoring from backup... failed.
[ARTIFACT] ID: JOMON-11 | Temp: 19C | Humidity:  60%  
[ANIMAL] Name:  Yuki | Diet: Mixed Nuts | Amount: 1.0kg | Time: 07:45
[SYS] WARN CPU Temp high
[ARTIFACT] ID: YAYOI-33 | Temp: 20C | Humidity: 48%
"""

    with open(os.path.join(logs_dir, "server_dump_1.log"), "w") as f:
        f.write(log_1.strip())
        
    with open(os.path.join(logs_dir, "sys_error_2.txt"), "w") as f:
        f.write(log_2.strip())
        
    with open(os.path.join(logs_dir, "backup_fail.log"), "w") as f:
        f.write(log_3.strip())

if __name__ == "__main__":
    build()
