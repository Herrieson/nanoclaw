import os
import csv
import json
import random

def build_env():
    # 初始化环境目录
    os.makedirs("dv_reports", exist_ok=True)
    farm_dir = "farm_server"
    os.makedirs(f"{farm_dir}/meta", exist_ok=True)
    
    total_jobs = 150
    target_job_id = random.randint(30, 120)  # 随机选一个作为真正的 Crash Job
    target_job_name = f"run_{target_job_id:03d}"
    
    # 构建 regression DB
    db_records = [["job_id", "test_name", "status", "start_time"]]
    
    test_names = ["ahb_sanity", "i2c_burst", "apb_rw_test", "dma_transfer_01", "sram_bist_test", "fullchip_axi_stress_001"]
    
    for i in range(total_jobs):
        job_id = f"run_{i:03d}"
        job_dir = f"{farm_dir}/{job_id}"
        os.makedirs(f"{job_dir}/logs", exist_ok=True)
        os.makedirs(f"{job_dir}/waves", exist_ok=True)
        os.makedirs(f"{job_dir}/debug", exist_ok=True)
        
        # 判断是否为目标 Job
        if i == target_job_id:
            t_name = "fullchip_axi_stress_001"
            status = "FATAL_CRASH"
            build_target_job(job_dir)
        else:
            # 制造干扰 Job
            t_name = random.choice(test_names)
            status = random.choice(["PASS", "UVM_ERROR", "TIMEOUT", "WARN"])
            if t_name == "fullchip_axi_stress_001" and status == "FATAL_CRASH":
                status = "TIMEOUT" # 保证目标唯一
            build_dummy_job(job_dir, status)
            
        db_records.append([job_id, t_name, status, f"2023-10-24 10:{i//10:02d}:{i%60:02d}"])
        
    # 写入 DB CSV
    with open(f"{farm_dir}/meta/regression_db.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(db_records)

def build_dummy_job(job_dir, status):
    # 生成随机无用日志
    with open(f"{job_dir}/logs/uvm_console.log", "w", encoding="utf-8") as f:
        f.write("UVM Simulation Started...\n")
        f.write("[UVM_INFO] Random stress started.\n")
        if status == "UVM_ERROR":
            f.write(f"[UVM_ERROR] @ {random.randint(1000, 9999) * 1000} ps: Data mismatch!\n")
        elif status == "TIMEOUT":
            f.write(f"[UVM_FATAL] @ 99999999 ps: Test timeout! (Watchdog fired)\n")
        f.write(f"Simulation Status: {status}\n")
    
    # 随便写点 mapping 混淆
    with open(f"{job_dir}/debug/signal_mapping.json", "w", encoding="utf-8") as f:
        json.dump({"!": "top.clk", "@": "top.rst_n"}, f)
        
    # 空的或无关的波形切片
    with open(f"{job_dir}/waves/dump_0_1000000.vcd", "w", encoding="utf-8") as f:
        f.write("#0\n1!\n1@\n#500\n0!\n")

def build_target_job(job_dir):
    crash_time = 45821000
    
    # 1. 构造真实的报错日志
    log_lines = ["[UVM_INFO] @ 0 ps: Simulator running..."]
    for t in range(1000000, crash_time - 1000000, 2500000):
        log_lines.append(f"[UVM_INFO] @ {t} ps: AXI monitor observed valid beat.")
        
    log_lines.append(f"[UVM_ERROR] @ {crash_time - 2500} ps: Protocol violation flag raised.")
    log_lines.append(f"UVM_FATAL @ {crash_time} ps: reporter [AXI_ASSERT_ERR] Unknown state (X/Z) detected on AXI bus payload! Simulation terminating immediately.")
    log_lines.append("Simulation CRASHED.")
    
    with open(f"{job_dir}/logs/uvm_console.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
        
    # 2. 构造剥离的 Mapping JSON
    # 使用奇葩的双字符代号增加匹配难度
    mapping = {
        "!#": "top_tb.dut.clk",
        "@$": "top_tb.dut.rst_n",
        "A1": "top_tb.dut.axi_interface.axi_awaddr",
        "B2": "top_tb.dut.axi_interface.axi_wdata",
        "C3": "top_tb.dut.axi_interface.axi_awvalid",
        "D4": "top_tb.dut.axi_interface.axi_awready", # 目标！
        "E5": "top_tb.dut.i2c_ctrl.i2c_sda",        # 诱饵（非AXI）
        "F6": "top_tb.dut.axi_interface.axi_wstrb",
        "G7": "top_tb.dut.sram_wrapper.sram_data"   # 诱饵
    }
    with open(f"{job_dir}/debug/signal_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
        
    # 3. 构造海量波形切片 (无 Header 的残缺 VCD 风格)
    # 切片区间：40000000 ~ 47000000，每 1000000 切一个文件
    start_t = 40000000
    end_t = 47000000
    chunk_size = 1000000
    
    for chunk_start in range(start_t, end_t, chunk_size):
        chunk_end = chunk_start + chunk_size
        filename = f"{job_dir}/waves/dump_{chunk_start}_{chunk_end}.vcd"
        
        with open(filename, "w", encoding="utf-8") as f:
            t = chunk_start
            while t < chunk_end:
                # 只在发生跳变的时间点写入 (模拟时钟)
                if t % 500 == 0:
                    f.write(f"#{t}\n")
                    f.write(f"{(t//500)%2}!#\n")
                    
                    # 随机数据翻转（填充噪音）
                    if t % 3500 == 0:
                        f.write(f"b{bin(random.randint(0, 0xFF))[2:]} A1\n")
                        f.write(f"b{bin(random.randint(0, 0xFFFF))[2:]} B2\n")
                    
                    # ----------------- 精准埋点逻辑 -----------------
                    # 诱饵 1：在很早之前，AXI线就有 X/Z，但不靠近崩溃时间点
                    if t == 41005000:
                        f.write("bx C3\n")
                        
                    # 诱饵 2：在崩溃前紧挨着的时间点，非 AXI 总线出现 X/Z (SRAM 或 I2C)
                    if t == 45820000:
                        f.write("bx E5\n") # I2C SDA
                        f.write("bz G7\n") # SRAM
                        
                    # ✅ 终极目标：在 UVM_FATAL (45821000) 的前一个时钟周期（45820500）出现 X 态的 AXI 线
                    if t == 45820500:
                        # axi_awready 被注入 X
                        f.write("bx D4\n")
                        
                    # 诱饵 3：在崩溃之后出现其他 X/Z
                    if t == 45821500:
                        f.write("bx F6\n")
                        
                t += 500

if __name__ == "__main__":
    build_env()
