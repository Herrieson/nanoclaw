import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("site_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("skills", exist_ok=True)

    # 1. 建立员工白名单
    roster = [
        "Mateo Hernandez",
        "Santiago Garcia",
        "Luis Rodriguez",
        "Carlos Martinez",
        "Juan Lopez"
    ]
    with open("master_roster.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(roster))

    # 2. 建立工地记录
    # 文件1: 模拟 PDF/图像 OCR 后的加密或占位文件
    # 内容预设为: 
    # Worker: Mateo Hernandez, Hours: 8, Material: 2 pillars broken
    # Worker: Luis Rodriguez, Hours: 10, Material: 0 pillars broken
    # Worker: Jose Ghost, Hours: 5, Material: 1 pillars broken
    with open("site_logs/monday_scan.pdf", "w", encoding="utf-8") as f:
        f.write("CONTENT_ENCRYPTED_SIGNATURE:OCR_REQUIRED_ID_7782")

    # 文件2: 西班牙语俚语混合记录
    # Jale = Hours/Work; Postes = Pillars; Roto = Broken
    log2 = """Fecha: 2023-10-02
Trabajador: Santiago Garcia, Jale: 12, Postes: 1 roto
Trabajador: Carlos Martinez, Jale: 8, Postes: 3 rotos
Trabajador: Unknown_Guy, Jale: 4, Postes: 0""" 
    with open("site_logs/tuesday_es.txt", "w", encoding="utf-8") as f:
        f.write(log2)

    # 文件3: 边缘情况
    log3 = "Juan Lopez | 6 hours | 0 pillars\nMateo Hernandez | 4 hours | 1 pillar"
    with open("site_logs/wednesday_extra.csv", "w", encoding="utf-8") as f:
        f.write(log3)

if __name__ == "__main__":
    build_env()
