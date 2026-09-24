import os
import argparse
import json
import csv
import random
from datetime import datetime, timedelta

def generate_fix_time(base_time, offset_ms):
    t = base_time + timedelta(milliseconds=offset_ms)
    return t.strftime("%Y%m%d-%H:%M:%S.%f")[:-3]

def build_turn_1():
    os.makedirs("market_data", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # 1. Config
    config_data = {
        "BTCUSD": {"bid_weight": 0.6, "ask_weight": 0.4},
        "ETHUSD": {"bid_weight": 0.5, "ask_weight": 0.5}
    }
    with open("config/trading_params.json", "w") as f:
        json.dump(config_data, f, indent=4)
        
    # 2. Fix Logs (t1) - 包含时间戳倒挂陷阱
    base_time = datetime(2023, 10, 27, 9, 30, 0)
    fix_logs = []
    
    # 正常序列 
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_001|55=BTCUSD|54=1|38=10|44=34000.5|52={generate_fix_time(base_time, 10)}|10=011")
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_002|55=ETHUSD|54=2|38=50|44=1800.2|52={generate_fix_time(base_time, 25)}|10=022")
    
    # 幽灵订单 1 (倒挂: 此时最大系统时间应为 offset 25, 但这个订单时间为 offset 15)
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_003_GHOST|55=BTCUSD|54=1|38=5|44=34010.0|52={generate_fix_time(base_time, 15)}|10=033")
    
    # 正常推移
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_004|55=BTCUSD|54=2|38=20|44=34005.0|52={generate_fix_time(base_time, 40)}|10=044")
    
    # 幽灵订单 2 (倒挂: 最大系统时间为 40, 该订单为 5)
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_005_GHOST|55=ETHUSD|54=1|38=100|44=1795.0|52={generate_fix_time(base_time, 5)}|10=055")
    
    # 正常推移
    fix_logs.append(f"8=FIX.4.4|9=112|35=D|11=ORD_006|55=BTCUSD|54=1|38=15|44=33990.0|52={generate_fix_time(base_time, 60)}|10=066")

    with open("market_data/fix_logs_t1.txt", "w") as f:
        for log in fix_logs:
            f.write(log + "\n")

    # 3. Order book snapshots
    snapshots = []
    # BTCUSD 快照
    snapshots.append([generate_fix_time(base_time, 0), "BTCUSD", 34000.0, 100, 34001.0, 150])
    snapshots.append([generate_fix_time(base_time, 12), "BTCUSD", 34002.0, 50, 34003.0, 200]) # 幽灵1 (offset 15) 会匹配这个
    snapshots.append([generate_fix_time(base_time, 30), "BTCUSD", 34005.0, 80, 34006.0, 120])
    
    # ETHUSD 快照
    snapshots.append([generate_fix_time(base_time, 0), "ETHUSD", 1800.0, 500, 1801.0, 400]) # 幽灵2 (offset 5) 会匹配这个
    snapshots.append([generate_fix_time(base_time, 20), "ETHUSD", 1798.0, 600, 1799.0, 300])

    with open("market_data/order_book_snapshots.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Symbol", "Bid1_Price", "Bid1_Vol", "Ask1_Price", "Ask1_Vol"])
        for snap in snapshots:
            writer.writerow(snap)

def build_turn_2():
    os.makedirs("risk_control", exist_ok=True)
    os.makedirs("market_data", exist_ok=True) # 确保存在此目录
    
    base_time = datetime(2023, 10, 27, 9, 30, 0)
    
    # 1. Executions (包含正常单和 Turn 1 的幽灵单)
    executions = []
    # 正常单成交
    executions.append(f"8=FIX.4.4|9=115|35=8|11=ORD_001|39=2|115=MM_ALPHA|52={generate_fix_time(base_time, 150)}|10=111")
    # 幽灵单1成交，涉及的做市商是 MM_SHADOW
    executions.append(f"8=FIX.4.4|9=115|35=8|11=ORD_003_GHOST|39=2|115=MM_SHADOW|52={generate_fix_time(base_time, 160)}|10=222")
    # 幽灵单2成交，涉及的做市商是 MM_VIPER
    executions.append(f"8=FIX.4.4|9=115|35=8|11=ORD_005_GHOST|39=2|115=MM_VIPER|52={generate_fix_time(base_time, 170)}|10=333")
    # 正常单被拒绝或未成交 (39=8 代表Rejected)
    executions.append(f"8=FIX.4.4|9=115|35=8|11=ORD_006|39=8|115=MM_ALPHA|52={generate_fix_time(base_time, 180)}|10=444")
    
    with open("market_data/executions_t2.txt", "w") as f:
        for ex in executions:
            f.write(ex + "\n")
            
    # 2. Alerts (只报特定的时间段，以此过滤违规者)
    alerts = []
    alerts.append(["ALERT_001", generate_fix_time(base_time, 155), generate_fix_time(base_time, 165), "LATENCY_ARBITRAGE_DETECTED"])
    # 故意漏掉 170 的时间段，使得 MM_VIPER 虽是幽灵单成交，但不在报警时间段内，不属于本次认定的黑手，测试 Agent 逻辑的严密性
    alerts.append(["ALERT_002", generate_fix_time(base_time, 200), generate_fix_time(base_time, 210), "SPOOFING_DETECTED"])
    
    with open("risk_control/alert_t2.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["AlertID", "StartTime", "EndTime", "AlertType"])
        for a in alerts:
            writer.writerow(a)

def build_turn_3():
    os.makedirs("settlement", exist_ok=True)
    
    # Clearance file
    clearance = []
    clearance.append(["TRD_1001", "MM_ALPHA", 50000.0])
    clearance.append(["TRD_1002", "MM_BETA", 12000.0])
    # 黑名单做市商的交易，应该被剥离
    clearance.append(["TRD_1003", "MM_SHADOW", -15000.0]) 
    clearance.append(["TRD_1004", "MM_SHADOW", 45000.0]) 
    # MM_VIPER 虽然参与了幽灵单，但在 Turn 2 中不符合警报时间段，不应被列为黑名单，应该保留其 PNL
    clearance.append(["TRD_1005", "MM_VIPER", 8000.0])
    clearance.append(["TRD_1006", "MM_GAMMA", -2000.0])

    with open("settlement/eod_clearance.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Trade_ID", "Maker_ID", "PNL"])
        for row in clearance:
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
