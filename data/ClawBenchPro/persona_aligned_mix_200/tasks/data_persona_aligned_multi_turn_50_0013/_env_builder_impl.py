import os
import argparse
import json

def build_turn_1():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    
    # 模拟 FIX 协议日志，包含残缺数据
    with open("raw_data/fix_logs_t1.txt", "w") as f:
        f.write("8=FIX.4.2|35=D|55=AAPL|54=1|38=100|44=150.25|10=123|\n") # valid
        f.write("8=FIX.4.2|35=D|55=MSFT|54=2|38=200|10=111|\n") # missing 44
        f.write("8=FIX.4.2|35=D|55=AAPL|54=2|38=50|44=150.30|10=222|\n") # valid
        f.write("8=FIX.4.2|35=D|55=MSFT|54=1|44=300.10|10=333|\n") # missing 38
        
    # 模拟 Order Book 脏数据，包含时间戳倒挂陷阱
    with open("raw_data/order_book_t1.csv", "w") as f:
        f.write("Timestamp,Symbol,BidPrice,BidSize,AskPrice,AskSize\n")
        f.write("1000000,AAPL,150.00,100,150.02,100\n") 
        f.write("1000500,AAPL,150.00,100,150.08,100\n") # Anomaly > 0.05
        f.write("1000400,AAPL,150.01,50,150.05,50\n") # Inversion by 100us (<1000us). Adjusted to 1000501. Spread=0.04
        f.write("998000,AAPL,150.00,10,150.02,10\n") # Inversion by 2501us (>1000us). Must be DROPPED.
        f.write("1001000,MSFT,300.00,50,300.03,50\n")

def build_turn_2():
    os.makedirs("compliance", exist_ok=True)
    os.makedirs("raw_data", exist_ok=True)
    
    # 第二轮增量数据
    # Agent必须使用第一轮的记忆来正确解析这批数据
    with open("raw_data/order_book_t2.csv", "w") as f:
        f.write("Timestamp,Symbol,BidPrice,BidSize,AskPrice,AskSize\n")
        f.write("2000000,AAPL,152.00,100,152.03,100\n")
        f.write("2000200,AAPL,152.00,100,152.07,100\n") # Anomaly > 0.05
        f.write("2000100,AAPL,152.01,100,152.05,100\n") # Inversion by 100us. Adjusted to 2000201. Spread=0.04
        f.write("2000500,MSFT,305.00,200,305.06,200\n") # Anomaly > 0.05
        f.write("2000400,MSFT,305.01,100,305.05,100\n") # Adjusted to 2000501. Spread=0.04
        
    with open("raw_data/executions_t2.csv", "w") as f:
        f.write("ExecID,Timestamp,Symbol,Side,Qty,Price\n")
        f.write("E1,2000050,AAPL,Buy,50,152.03\n") 
        f.write("E2,2000200,AAPL,Sell,100,152.00\n") # Caught in anomaly.
        f.write("E3,2000201,AAPL,Buy,50,152.05\n") # Poison Pill! If inversion isn't fixed, it flags as anomaly incorrectly.
        f.write("E4,2000500,MSFT,Buy,100,305.06\n") # Caught in anomaly.
        f.write("E5,2000550,MSFT,Sell,50,305.00\n") # Matches to 2000501. Normal.

def build_turn_3():
    os.makedirs("risk", exist_ok=True)
    impact = {
        "AAPL": {"slippage_multiplier": 1.5},
        "MSFT": {"slippage_multiplier": 2.0}
    }
    with open("risk/market_impact.json", "w") as f:
        json.dump(impact, f, indent=4)

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
