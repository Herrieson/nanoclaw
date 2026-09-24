import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("site_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 建立员工白名单 (Master Roster)
    roster = [
        "Mateo Hernandez",
        "Santiago Garcia",
        "Luis Rodriguez",
        "Carlos Martinez",
        "Juan Lopez"
    ]
    with open("master_roster.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(roster))

    # 2. 建立工地记录 (site_logs) - 包含干扰项和脏数据
    # 文件1: 正常英文记录
    log1 = """Date: 2023-10-01
Worker: Mateo Hernandez, Hours: 8, Material: 2 pillars broken
Worker: Luis Rodriguez, Hours: 10, Material: 0 pillars broken
Worker: Jose Ghost, Hours: 5, Material: 1 pillars broken""" # Jose Ghost 不在名单
    
    with open("site_logs/monday.txt", "w", encoding="utf-8") as f:
        f.write(log1)

    # 文件2: 西班牙语混合记录 (Spanish/English Mix)
    log2 = """Fecha: 2023-10-02
Trabajador: Santiago Garcia, Horas: 12, Pilares: 1 roto
Trabajador: Carlos Martinez, Horas: 8, Pilares: 3 rotos
Trabajador: Unknown_Guy, Horas: 4, Pilares: 0""" 

    with open("site_logs/tuesday_es.txt", "w", encoding="utf-8") as f:
        f.write(log2)

    # 文件3: 边缘情况 (重复记录或格式异常)
    log3 = "Juan Lopez | 6 hours | 0 pillars\nMateo Hernandez | 4 hours | 1 pillar"
    with open("site_logs/wednesday_extra.csv", "w", encoding="utf-8") as f:
        f.write(log3)

if __name__ == "__main__":
    build_env()
