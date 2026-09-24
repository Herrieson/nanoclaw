import os
import random

def build_env():
    # 创建所有必需的目录层级
    os.makedirs("sim_output", exist_ok=True)
    os.makedirs("hw_design", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 构建二进制加密的信号与模块映射数据库 (Agent 无法直接 cat 读取)
    # 强制 Agent 调用查询 Skill
    with open("hw_design/signal_mapping.enc", "wb") as f:
        # 写入文件头伪装成加密格式
        f.write(b"EDA_NETLIST_ENC_DB_V9\x00\x01\x04")
        # 写入大量随机不可见字符，直接 cat 会乱码并扰乱 terminal
        f.write(os.urandom(8192))
        f.write(b"\xDE\xAD\xBE\xEF") # 伪造的结束符
        
    # 2. 构建专有格式的二进制波形文件 (Agent 无法直接 cat 读取)
    # 强制 Agent 调用波形解析 Skill
    with open("sim_output/wave_dump.fsdb", "wb") as f:
        f.write(b"FSDB_V5_HEADER\x00\x00\x00\x00")
        f.write(os.urandom(10240))
        f.write(b"END_OF_FSDB_STREAM\x00")

    # 3. 构建报错日志以提供线索与代入感
    with open("logs/regression_nightly.err", "w", encoding="utf-8") as f:
        f.write("UVM_FATAL @ SIM_TIME: 479000 ps: reporter [AXI_PROTOCOL_ERR] Protocol violation detected on AW channel.\n")
        f.write("Reason: Unknown logic state (X-propagation) observed on AXI address bus during a valid transaction cycle.\n")
        f.write("Fatal Action: Simulation terminated abruptly to prevent further corrupted states.\n")
        f.write("Hint: Check sim_output/wave_dump.fsdb backwards from 479000 ps to isolate the exact injection cycle.\n")

if __name__ == "__main__":
    build_env()
