import os
import random
import struct

def build_env():
    # 建立必要的目录结构
    os.makedirs("sim_data", exist_ok=True)
    os.makedirs("dv_reports", exist_ok=True)

    # 1. 生成 VCS 仿真日志文件 (保持明文，供提取时间戳)
    log_content = [
        "Chronologic VCS simulator copyright 1991-2023",
        "Compiler version U-2023.03-SP2_Full64; Runtime version U-2023.03-SP2_Full64;  Oct 24 02:13 2023",
        "Loading design...",
        "Design loaded successfully.",
        "Starting UVM phasing...",
        "[UVM_INFO] @ 0 ps: reporter [RNTST] Running test axi_random_stress_test...",
        "Memory initialization completed.",
    ]
    
    # 插入一堆干扰日志
    for i in range(1, 150):
        t = i * 10000
        addr = hex(random.randint(0, 0xFFFFFFFF))
        log_content.append(f"[UVM_INFO] @ {t} ps: uvm_test_top.env.axi_agent.monitor [AXI_MON] Transaction observed at address {addr}")
        if i % 17 == 0:
            log_content.append(f"[UVM_WARNING] @ {t + 2500} ps: uvm_test_top.env.scoreboard [SCB_WARN] Delayed response detected.")

    # 插入 Fatal Error
    fatal_time = 1425000
    log_content.append(f"[UVM_ERROR] @ {fatal_time} ps: uvm_test_top.env.axi_agent.driver [AXI_DRV] Protocol violation!")
    log_content.append(f"UVM_FATAL @ {fatal_time} ps: reporter [AXI_ASSERT_ERR] Unknown state (X/Z) detected on AXI bus payload! Simulation terminating immediately.")
    log_content.append("--- UVM Report Summary ---")
    log_content.append("** Report counts by severity")
    log_content.append("UVM_INFO : 152")
    log_content.append("UVM_WARNING : 8")
    log_content.append("UVM_ERROR : 1")
    log_content.append("UVM_FATAL : 1")
    
    with open("sim_data/vcs_sim.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_content) + "\n")

    # 2. 生成假的 FSDB (Fast Signal Database) 二进制文件
    # FSDB 是高压缩比的二进制波形文件格式，文本工具无法读取。
    # 我们用结构化的随机二进制数据去 Mock，迫使 Agent 使用特定的解析 Skill
    with open("sim_data/wave_dump.fsdb", "wb") as f:
        # 写入伪造的 FSDB 文件头 (Magic Bytes)
        f.write(b"FSDB_VCS_DUMP\x00\x01\x00\x00")
        
        # 填充无意义的二进制压缩块数据
        for _ in range(5000):
            # 写入随机的 float 和 int 混淆数据，模拟高密度波形结构
            f.write(struct.pack('>f', random.uniform(-1.0, 1.0)))
            f.write(struct.pack('>I', random.randint(0, 4294967295)))
        
        # 文件尾部校验码
        f.write(b"EOF\x00\xff\xff\xff\xff")

if __name__ == "__main__":
    build_env()
