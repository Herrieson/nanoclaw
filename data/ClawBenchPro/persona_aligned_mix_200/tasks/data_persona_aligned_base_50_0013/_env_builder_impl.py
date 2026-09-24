import os
import random

def build_env():
    # 创建运行时目录结构
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("gateway_dump", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    random.seed(8848)
    symbols = ["AAPL", "GOOG", "TSLA", "MSFT", "NVDA", "TRAP_SYM", "FAT_FINGER_X"]

    # 生成极其非标准的 L2 Order Book 数据
    # 格式: TS \x01 SYMBOL \x01 Bids \x01 Asks
    with open("snapshots/l2_orderbook.dat", "w", encoding="utf-8") as f:
        # 写入干扰的头部和乱码
        f.write("0xDEADBEEF [UDP_MULTICAST_INIT] STARTING SEQUENCE\n")
        f.write("WARN: GAP DETECTED IN SEQUENCE 9812-9815\n")
        
        t = 1698000000000000000
        max_t = t
        
        for i in range(150):
            # 正常的时间流逝
            t += random.randint(10000, 50000)
            max_t = max(max_t, t)
            
            sym = random.choice(symbols[:5])
            
            # 生成正常的买卖盘 (买价低于卖价)
            bid1 = random.uniform(100.0, 500.0)
            ask1 = bid1 + random.uniform(0.1, 1.5)
            
            bids = f"{bid1:.2f}:100|{bid1-0.1:.2f}:200|{bid1-0.2:.2f}:150"
            asks = f"{ask1:.2f}:100|{ask1+0.1:.2f}:200|{ask1+0.2:.2f}:150"
            
            f.write(f"{t}\x01{sym}\x01{bids}\x01{asks}\n")
            
            # 制造干扰陷阱 1: 时间戳倒挂，且数据属于正常盘面
            if i == 45:
                t_trap = max_t - 80000  # 落后的乱序包
                f.write(f"{t_trap}\x01{sym}\x01{bids}\x01{asks}\n")
                
            # 制造干扰陷阱 2: 时间戳倒挂，且包含了买卖盘倒挂 (Agent如果不做单调性校验就会踩坑)
            if i == 85:
                t_trap = max_t - 150000  # 严重落后的乱序包
                trap_bid = 300.50
                trap_ask = 300.00  # Crossed!
                bids_trap = f"{trap_bid:.2f}:50|{trap_bid-0.1:.2f}:100"
                asks_trap = f"{trap_ask:.2f}:50|{trap_ask+0.1:.2f}:100"
                f.write(f"{t_trap}\x01TRAP_SYM\x01{bids_trap}\x01{asks_trap}\n")
                
            # 真正的异常: 时间戳正常递增，且发生了买卖盘倒挂
            if i == 112:
                t += 20000
                max_t = max(max_t, t)
                real_bid = 185.00
                real_ask = 184.50  # 真实引发熔断的 Crossed Book!
                bids_real = f"{real_bid:.2f}:500|{real_bid-0.5:.2f}:1000"
                asks_real = f"{real_ask:.2f}:500|{real_ask+0.5:.2f}:1000"
                f.write(f"{t}\x01FAT_FINGER_X\x01{bids_real}\x01{asks_real}\n")
                
            # 偶尔混入网关解析失败的底层 HEX 报错
            if i % 40 == 0:
                f.write(f"ERR_DECODE \x01 0x7F8C9B \x01 ILLEGAL_SOH_TAG \x01 NULL\n")

        f.write("0xEOF [CONNECTION_TERMINATED]\n")

    # 生成辅助/噪音日志
    with open("gateway_dump/fix_raw.log", "w", encoding="utf-8") as f:
        f.write("20231024-08:00:00.000 [WARN] UDP buffer full, starting to drop packets\n")
        f.write("8=FIX.4.4\x019=122\x0135=D\x0149=CLIENT1\x0156=EXCHANGE\x0134=213\x0152=20231024-08:00:00.001\x0111=ID992\x0121=1\x0155=NVDA\x0154=1\x0138=100\x0140=2\x0144=150.25\x0110=192\x01\n")
        f.write("20231024-08:00:00.050 [FATAL] L2 MATCHING ENGINE CIRCUIT BREAKER ENGAGED. CROSSED BOOK DETECTED IN SNAPSHOT STREAM.\n")
