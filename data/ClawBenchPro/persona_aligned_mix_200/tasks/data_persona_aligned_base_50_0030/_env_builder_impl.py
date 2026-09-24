import os
import random

def build_env():
    # 建立必要的目录结构
    os.makedirs("sim_data", exist_ok=True)
    os.makedirs("dv_reports", exist_ok=True)

    # 1. 生成 VCS 仿真日志文件
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

    # 2. 生成 VCD (Value Change Dump) 文件
    # VCD 文件格式是一种文本波形标准，含有头部声明和随时间变化的值。
    vcd_header = """$date
   Oct 24, 2023 03:15:22
$end
$version
   VCS U-2023.03-SP2
$end
$timescale
   1 ps
$end
$scope module top_tb $end
$scope module dut $end
$scope module axi_interface $end
$var wire 1 ! clk $end
$var wire 1 " rst_n $end
$var wire 32 # axi_awaddr $end
$var wire 64 $ axi_wdata $end
$var wire 1 % axi_awvalid $end
$var wire 1 & axi_awready $end
$var wire 8 ' axi_wstrb $end
$upscope $end
$upscope $end
$upscope $end
$enddefinitions $end
$dumpvars
0!
1"
b00000000000000000000000000000000 #
b0000000000000000000000000000000000000000000000000000000000000000 $
0%
0&
b00000000 '
$end
"""
    
    with open("sim_data/wave_dump.vcd", "w", encoding="utf-8") as f:
        f.write(vcd_header)
        
        # 制造时钟和信号跳变 (Clock period = 1000ps)
        current_time = 1350000 # 仅截取最后一段波形
        
        while current_time <= fatal_time + 2000:
            f.write(f"#{current_time}\n")
            
            # 翻转时钟
            clk_val = (current_time // 500) % 2
            f.write(f"{clk_val}!\n")
            
            # 在某些随机时间跳变总线信号（制造大量的干扰数据）
            if current_time % 3000 == 0:
                f.write(f"b{bin(random.randint(0, 0xFFFFFFFF))[2:]} #\n")
            if current_time % 2500 == 0:
                f.write(f"b{bin(random.randint(0, 0xFFFFFFFFFFFFFFFF))[2:]} $\n")
            if current_time % 7000 == 0:
                f.write(f"{random.randint(0,1)}%\n")
                f.write(f"{random.randint(0,1)}&\n")
            
            # 在另一个不相干的时间点制造 Z 态（作为高级干扰项）
            if current_time == 1385000:
                f.write("bz '\n")
                
            # 埋入关键 Bug！
            # 崩溃时间是在 1425000 ps，所以在 1424500 ps (前一个时钟跳变点) 发生异常 X 态
            if current_time == 1424500:
                # axi_wdata 被灌入了不定态 X
                f.write("bx $\n")
                
            current_time += 500

if __name__ == "__main__":
    build_env()
