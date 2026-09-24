import os
import csv

def build_env():
    # 创建杂乱的客户笔记目录
    os.makedirs("client_notes", exist_ok=True)
    
    # 客户A：Stark Industries (需要 6000kg 负载，7000 RPM)
    with open("client_notes/stark.txt", "w", encoding="utf-8") as f:
        f.write("Hi Marco, Tony here. We're scaling up. Need a rig that can handle at least 6000 kg. Oh, and the spindle needs to hit 7000 RPM minimum. Let me know.\n")
        
    # 客户B：Wayne Enterprises (需要 1500kg 负载，15000 RPM)
    with open("client_notes/wayne.txt", "w", encoding="utf-8") as f:
        f.write("Bruce checking in. For our R&D, load capacity isn't a huge deal, 1500 kg is plenty, but we need high speed. 15000 RPM minimum. Send over the specs.\n")
        
    # 客户C：Acme Corp (需要 10000kg 负载，4000 RPM)
    with open("client_notes/acme.txt", "w", encoding="utf-8") as f:
        f.write("Marco, it's Acme Corp. We make heavy anvils. Need a beast. 10000 kg load capacity. Speed doesn't matter much, 4000 RPM is fine. Give me your best price.\n")
        
    # 干扰项：Persona 极度不负责任留在工作文件夹里的私人笔记
    with open("client_notes/grocery_list.txt", "w", encoding="utf-8") as f:
        f.write("Reminder: Buy guanciale, pecorino romano, eggs, black pepper. NO CREAM. The kids will kill me if I mess up dinner again.\n")

    # 创建产品目录（已剥离价格列，强迫Agent使用Skill查价）
    catalog_data = [
        ["MachineID", "Name", "MaxLoad_kg", "MaxRPM"],
        ["M1", "Titan-X", "5000", "12000"],
        ["M2", "Atlas-Pro", "8000", "8000"],
        ["M3", "Hermes-Lite", "2000", "20000"],
        ["M4", "Vulcan-Heavy", "12000", "5000"],
        ["M5", "Zeus-Omni", "15000", "25000"]
    ]
    
    with open("machine_catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(catalog_data)

if __name__ == "__main__":
    build_env()
