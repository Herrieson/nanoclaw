import os
import random
import json
import uuid

def build_env():
    # 设定全局随机种子
    random.seed(8848)

    # 1. 建立极其复杂的目录树结构
    os.makedirs("ops", exist_ok=True)
    os.makedirs("var/logs/risk_engine", exist_ok=True)
    os.makedirs("var/data/udp_ingest", exist_ok=True)
    os.makedirs("etc/reference_data/instruments/equities/tech", exist_ok=True)
    os.makedirs("etc/reference_data/instruments/equities/finance", exist_ok=True)
    os.makedirs("etc/reference_data/instruments/crypto", exist_ok=True)
    os.makedirs("etc/reference_data/backup_old", exist_ok=True)

    # 2. 生成 Instrument 映射数据 (制造碎片化 JSON)
    instruments = {
        1001: ("AAPL", "equities/tech"),
        1002: ("GOOG", "equities/tech"),
        1003: ("TSLA", "equities/tech"),
        1004: ("MSFT", "equities/tech"),
        1005: ("NVDA", "equities/tech"),
        1006: ("FAT_FINGER_X", "equities/finance"), # 真正发生倒挂的
        1007: ("JPM", "equities/finance"),
        1008: ("TRAP_SYM", "crypto"),               # 假陷阱
        1009: ("DOGE", "crypto")
    }
    
    for inst_id, (sym, category) in instruments.items():
        filepath = f"etc/reference_data/instruments/{category}/inst_{inst_id}.json"
        with open(filepath, "w") as f:
            json.dump({"instrument_id": inst_id, "symbol": sym, "active": True}, f)
            
    # 干扰项
    for i in range(2000, 2010):
        with open(f"etc/reference_data/backup_old/inst_{i}.json", "w") as f:
            json.dump({"instrument_id": i, "symbol": f"OBSOLETE_{i}", "active": False}, f)

    # 3. 生成系统告警日志 (藏有真实的 Session ID)
    true_session = "sess_f49a2_prod"
    decoy_session = "sess_b831c_test"
    
    with open("var/logs/risk_engine/syslog_20231024.log", "w", encoding="utf-8") as f:
        f.write("08:00:01.000 [INFO] System startup initialized.\n")
        f.write("08:05:12.331 [WARN] High memory usage detected.\n")
        f.write(f"08:10:05.112 [ERROR] Dropped packets in session {decoy_session}\n")
        f.write(f"08:15:33.901 [WARN] CROSSED BOOK DETECTED IN TEST ENV. IGNORING. SOURCE: {decoy_session}\n")
        f.write("08:20:00.000 [INFO] End of Day processing started for region APAC.\n")
        # 夹杂数千行无用日志
        for _ in range(3000):
            f.write(f"08:21:{random.randint(10,59)}.000 [DEBUG] Heartbeat received from downstream.\n")
        f.write(f"08:45:12.999 [FATAL] L2 MATCHING ENGINE CIRCUIT BREAKER ENGAGED. SOURCE: {true_session}\n")
        for _ in range(500):
            f.write(f"08:45:{random.randint(13,59)}.000 [ERROR] Connection refused. Engine stopped.\n")

    # 4. 生成 L2 快照碎片数据函数
    def generate_session_data(session_name, is_true_session):
        os.makedirs(f"var/data/udp_ingest/{session_name}", exist_ok=True)
        
        t = 1698000000000000000
        max_t = t
        
        total_records = 3000
        records_per_file = 50
        
        # 预设异常位置
        trap_index = 850
        real_crash_index = 2112 if is_true_session else -1
        
        records = []
        for i in range(total_records):
            # 正常时间流逝
            t += random.randint(10000, 50000)
            max_t = max(max_t, t)
            
            inst_id = random.choice([1001, 1002, 1003, 1004, 1005, 1007, 1009])
            
            bid1 = random.uniform(100.0, 500.0)
            ask1 = bid1 + random.uniform(0.1, 1.5)
            
            # 生成陷阱：乱序包且发生倒挂（会被时间戳单调性校验过滤掉）
            if i == trap_index:
                t_trap = max_t - 200000 # 严重落后的乱序包
                trap_bid = 300.50
                trap_ask = 300.00 # Crossed!
                bids = f"{trap_bid:.2f}:50|{trap_bid-0.1:.2f}:100"
                asks = f"{trap_ask:.2f}:50|{trap_ask+0.1:.2f}:100"
                records.append(f"{t_trap}\x011008\x01{bids}\x01{asks}\n")
                continue
                
            # 真实的灾难：时间戳递增，真实倒挂
            if i == real_crash_index:
                t += 20000
                max_t = max(max_t, t)
                real_bid = 185.00
                real_ask = 184.50 # 真实 Crossed Book
                bids = f"{real_bid:.2f}:500|{real_bid-0.5:.2f}:1000"
                asks = f"{real_ask:.2f}:500|{real_ask+0.5:.2f}:1000"
                records.append(f"{t}\x011006\x01{bids}\x01{asks}\n")
                continue
            
            # 制造一些普通的乱序正常包干扰
            current_t = t
            if random.random() < 0.05: # 5% 的包是乱序延迟的
                current_t = max_t - random.randint(50000, 100000)

            bids = f"{bid1:.2f}:100|{bid1-0.1:.2f}:200|{bid1-0.2:.2f}:150"
            asks = f"{ask1:.2f}:100|{ask1+0.1:.2f}:200|{ask1+0.2:.2f}:150"
            
            # 偶尔加入网关解析失败的乱码
            if i % 103 == 0:
                records.append(f"ERR_DECODE \x01 0x7F8C9B \x01 ILLEGAL_SOH_TAG \x01 NULL\n")
            else:
                records.append(f"{current_t}\x01{inst_id}\x01{bids}\x01{asks}\n")
                
        # 将记录分片写入文件
        for seq_idx in range(0, total_records, records_per_file):
            chunk = records[seq_idx : seq_idx + records_per_file]
            file_name = f"var/data/udp_ingest/{session_name}/frag_{seq_idx//records_per_file:04d}.dat"
            with open(file_name, "w", encoding="utf-8") as f:
                f.writelines(chunk)

    # 5. 执行数据生成
    generate_session_data(decoy_session, is_true_session=False)
    generate_session_data(true_session, is_true_session=True)

if __name__ == "__main__":
    build_env()
