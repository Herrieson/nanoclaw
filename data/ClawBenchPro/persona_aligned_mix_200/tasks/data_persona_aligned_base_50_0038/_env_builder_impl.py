import os
import random

def build_env():
    # 创建所有必需的目录层级
    os.makedirs("sim_output", exist_ok=True)
    os.makedirs("hw_design", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 构建混乱的信号与模块映射数据库 (干扰极大，非标准分隔符)
    with open("hw_design/signal_mapping.db", "w", encoding="utf-8") as f:
        f.write("## EDA_NETLIST_EXTRACTOR v9.4.1a_BETA (Obfuscated Build)\n")
        f.write("## FORMAT: // INSTANCE_PATH \\\\ ---> << SIG1, SIG2, ... >>\n\n")
        
        # 写入随机干扰数据
        for i in range(1, 450):
            mod = f"sys_top.domain_cpu.subsys_{i}.random_blk_{random.randint(10,99)}"
            sigs = [f"sig_wire_{random.randint(1000,9999)}" for _ in range(random.randint(3, 8))]
            f.write(f"// {mod} \\\\ ---> << {', '.join(sigs)} >>\n")
            if i % 42 == 0:
                f.write("%% CORRUPTED_BLOCK_ENTRY_SKIPPED %%\n")

        # 写入目标模块与信号映射
        target_module = "sys_top.bus_matrix.u_axi_interconnect_m0"
        f.write(f"// {target_module} \\\\ ---> << axi_awvalid, axi_awaddr, axi_awburst, axi_awlen >>\n")

        # 继续写入随机干扰数据
        for i in range(451, 900):
            mod = f"sys_top.domain_periph.subsys_{i}.random_blk_{random.randint(10,99)}"
            sigs = [f"sig_wire_{random.randint(1000,9999)}" for _ in range(random.randint(2, 6))]
            f.write(f"// {mod} \\\\ ---> << {', '.join(sigs)} >>\n")

    # 2. 构建海量的非标准 ASCII 波形文件
    target_time = 478230
    with open("sim_output/wave_ascii_dump.trace", "w", encoding="utf-8") as f:
        f.write("=== Xcelium ASCII Waveform Dump (Custom DV Tool) ===\n")
        f.write("START TIME: 0 ps\n")
        f.write("RESOLUTION: 10 ps\n")
        f.write("WARNING: Timing violations may result in X/Z states.\n\n")

        time_ps = 0
        # 写入正常状态的时序波形
        while time_ps < target_time:
            f.write(f"@[{time_ps}]\n")
            f.write(f"  sys_clk: {1 if (time_ps//10)%2 == 0 else 0}\n")
            f.write(f"  axi_awaddr: 32'h{random.randint(10000000, 99999999):08X}\n")
            f.write(f"  axi_awvalid: {random.choice(['1', '0'])}\n")
            time_ps += 10
            
        # 注入致命的 X 态异常跳变
        f.write(f"@[{target_time}]\n")
        f.write(f"  sys_clk: {1 if (target_time//10)%2 == 0 else 0}\n")
        f.write(f"  axi_awaddr: 32'hA0X0_1234\n") # X 态在这里首次出现
        f.write(f"  axi_awvalid: 1\n")
        
        time_ps += 10

        # 后续产生级联传播的未知状态
        for _ in range(300):
            f.write(f"@[{time_ps}]\n")
            f.write(f"  sys_clk: {1 if (time_ps//10)%2 == 0 else 0}\n")
            f.write(f"  axi_awaddr: 32'hXXXX_XXXX\n")
            f.write(f"  axi_awvalid: X\n")
            time_ps += 10

    # 3. 构建报错日志以提供线索与代入感
    with open("logs/regression_nightly.err", "w", encoding="utf-8") as f:
        f.write("UVM_FATAL @ SIM_TIME: 479000 ps: reporter [AXI_PROTOCOL_ERR] Protocol violation detected on AW channel.\n")
        f.write("Reason: Unknown logic state (X-propagation) observed on AXI address bus during a valid transaction cycle.\n")
        f.write("Fatal Action: Simulation terminated abruptly to prevent further corrupted states.\n")
        f.write("Hint: Check sim_output/wave_ascii_dump.trace backwards from 479000 ps to isolate the exact injection cycle.\n")

if __name__ == "__main__":
    build_env()
