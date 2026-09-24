import os
import random
import uuid

def build_env():
    # 创建复杂的深渊目录树
    os.makedirs("sim_output/wave_dumps", exist_ok=True)
    os.makedirs("hw_design/db_backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 核心目标数据生成
    target_signal = "axi_awaddr_m7"
    target_hash = uuid.uuid4().hex[:8]
    target_time = 643210
    target_module = "sys_top.bus_matrix.u_axi_interconnect_m7_core_inst"

    # 1. 制造日志文件 (提供两段关键线索)
    with open("logs/regression_nightly.err", "w", encoding="utf-8") as f:
        f.write("[FATAL] UVM_ERROR at 650000 ps\n")
        f.write(f"[AXI_PROTOCOL] Target bus '{target_signal}' detected illegal state transition.\n")
        f.write("[HINT] Waveform dumped in unordered chunks. Find the absolute FIRST injection cycle.\n")

    with open("logs/build_info.txt", "w", encoding="utf-8") as f:
        f.write("--- NIGHTLY BUILD METADATA ---\n")
        f.write("Date: 2024-11-12\n")
        f.write("RTL_TAG: RC_3.9.1\n")
        f.write(f"DB_HASH: {target_hash}\n")
        f.write("Warning: Do not use deprecated databases!\n")

    # 2. 制造海量 db_backups (噪音与诱饵，500个文件)
    db_indices = list(range(1, 501))
    target_db_idx = random.choice(db_indices) # 随机隐藏真正的 DB

    for i in db_indices:
        is_target = (i == target_db_idx)
        file_hash = target_hash if is_target else uuid.uuid4().hex[:8]
        # 如果找错了 DB，会拿到带有 deprecated 的错误模块名
        module_name = target_module if is_target else f"sys_top.bus_matrix.deprecated_v{i}.axi_m7"
        
        with open(f"hw_design/db_backups/mapping_v{i}.db", "w", encoding="utf-8") as f:
            f.write("## EDA_NETLIST_EXTRACTOR v10.0\n")
            f.write(f"## DB_HASH: {file_hash}\n")
            f.write("## FORMAT: // INSTANCE_PATH \\\\ ---> << SIG1, SIG2, ... >>\n\n")
            
            # 干扰数据
            for j in range(4):
                f.write(f"// sys_top.dummy.block_{j} \\\\ ---> << axi_awaddr_m{j}, axi_awvalid_m{j} >>\n")
            
            # 注入目标信号映射 (真假混合)
            f.write(f"// {module_name} \\\\ ---> << axi_awvalid_m7, {target_signal}, axi_awburst_m7 >>\n")
            
            # 干扰数据
            for j in range(8, 12):
                f.write(f"// sys_top.dummy.block_{j} \\\\ ---> << axi_awaddr_m{j} >>\n")

    # 3. 制造碎片化、乱序的波形文件
    # 时间轴：从 0 到 1,000,000 ps，步长 10 ps
    # 切成 200 个文件，每个包含 500 个时间步
    file_chunks = []
    for chunk_id in range(200):
        start_time = chunk_id * 5000
        file_chunks.append(start_time)
    
    # 致命陷阱：彻底打乱时间轴与文件编号的映射关系
    random.shuffle(file_chunks) 
    
    for fake_id, start_time in enumerate(file_chunks):
        with open(f"sim_output/wave_dumps/wave_chunk_{fake_id:03d}.trace", "w", encoding="utf-8") as f:
            for step in range(500):
                t = start_time + step * 10
                f.write(f"@[{t}]\n")
                f.write(f"  sys_clk: {1 if (t//10)%2 == 0 else 0}\n")
                
                # 陷阱：其他信号经常出现 'X' 态，干扰无脑 grep 'X' 的行为
                if random.random() < 0.15:
                    f.write(f"  axi_awaddr_m3: 32'hXXXX_XXXX\n")
                
                # 目标信号状态逻辑
                if t < target_time:
                    # 绝对正常，生成标准的十六进制(不会含有 X)
                    val = f"{random.randint(0, 0xFFFFFFFF):08X}"
                    f.write(f"  {target_signal}: 32'h{val}\n")
                elif t == target_time:
                    # 第一次注入非法未知态 X
                    f.write(f"  {target_signal}: 32'hA0X0_1234\n")
                else:
                    # 后续时间点产生级联污染，全部带有 X
                    f.write(f"  {target_signal}: 32'hXXXX_XXXX\n")

if __name__ == "__main__":
    build_env()
