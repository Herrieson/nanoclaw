import os
import random
import time

def build_env():
    # Create directory structure
    os.makedirs("syslog", exist_ok=True)
    os.makedirs("risk_control", exist_ok=True)
    
    # 1. Setup crash context
    symbols = ["AAPL", "TSLA", "XIN9", "YNG2", "ZOMG", "VIX_OPT", "BOGUS"]
    crash_symbol = "ZOMG"
    poison_bid_px = 9988.5
    crash_ts = 1718005500123456
    
    with open(os.path.join("syslog", "kernel_panic.log"), "w", encoding="utf-8") as f:
        f.write("[08:00:01.000] systemd: Starting High Frequency Engine...\n")
        f.write("[08:15:33.111] NET_GW: TCP connection established.\n")
        f.write("[08:45:12.999] [WARN] Micro-structure buffer utilization at 85%\n")
        f.write(f"[08:45:13.001] [FATAL] Division by zero in spread calculator!\n")
        f.write(f"[08:45:13.001] [FATAL] Engine died at approx TS={crash_ts} while processing symbol {crash_symbol}!\n")
        f.write("[08:45:13.005] [DUMP] Flushing remaining L2 memory to fragmented nodes in dumps/ shard directories...\n")
        f.write("[08:45:13.006] System halted.\n")

    # 2. Generate fragmented dumps (Order Book Snapshots)
    for shard in range(16):
        shard_dir = os.path.join("dumps", f"shard_{shard:02d}")
        os.makedirs(shard_dir, exist_ok=True)
        
        for file_idx in range(5):
            dump_file = os.path.join(shard_dir, f"mem_snap_0x{random.randint(0, 0xFFFFFF):06x}.dat")
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write("0xDEADBEEF L2 DUMP START\n")
                f.write("FMT_V2: TS||SYM||BIDS[px@vol,px@vol...]||ASKS[px@vol,px@vol...]\n")
                
                for _ in range(100):
                    sym = random.choice(symbols)
                    ts = crash_ts - random.randint(100000, 900000)
                    
                    # Normal spread
                    b1, a1 = 3000.0, 3001.0
                    
                    # Decoy 1: Valid inversion for Options
                    if sym == "VIX_OPT" and random.random() < 0.1:
                        b1, a1 = 50.0, 48.0 # Negative spread but valid for this symbol
                    
                    # Decoy 2: Different symbol abnormal bid
                    if sym == "BOGUS" and random.random() < 0.05:
                        b1, a1 = 8000.0, 3000.0
                        
                    bids = f"{b1}@100,{b1-1}@200,{b1-2}@50"
                    asks = f"{a1}@50,{a1+1}@150,{a1+2}@200"
                    f.write(f"{ts}||{sym}||{bids}||{asks}\n")
                
                # INJECT POISON SNAPSHOT exactly once in a specific shard
                if shard == 7 and file_idx == 3:
                    bids = f"{poison_bid_px}@500,2995.0@100" # Poison Bid
                    asks = f"3000.0@20,3001.0@50"            # Normal Ask
                    f.write(f"{crash_ts}||{crash_symbol}||{bids}||{asks}\n")
                
                f.write("<<EOF>>\n")

    # 3. Generate corrupted network traffic logs
    os.makedirs("network_traffic", exist_ok=True)
    SOH = '\x01'
    
    def make_fix_msg(sender, target, seq, clordid, symbol, msg_type, side, price, qty):
        # 35=MsgType (D=NewOrderSingle, 8=ExecutionReport, W=MarketData)
        # 54=Side (1=Buy, 2=Sell)
        body = f"35={msg_type}{SOH}49={sender}{SOH}56={target}{SOH}34={seq}{SOH}11={clordid}{SOH}55={symbol}{SOH}54={side}{SOH}44={price}{SOH}38={qty}{SOH}"
        msg = f"8=FIX.4.2{SOH}9={len(body)}{SOH}{body}10={random.randint(100,255):03d}{SOH}"
        return msg.encode('ascii')

    seq_num = 1
    for stream in range(20):
        stream_file = os.path.join("network_traffic", f"eth0_stream_{stream:02d}.pcap.raw")
        with open(stream_file, "wb") as f:
            for _ in range(150):
                # Write TCP binary garbage
                f.write(os.urandom(random.randint(5, 50)))
                f.write(b"TCP_FRAG_ERR")
                
                sym = random.choice(symbols)
                px = round(random.uniform(100.0, 5000.0), 1)
                
                # Normal orders
                msg = make_fix_msg(f"FIRM_{random.randint(1,99)}", "EXCHANGE", seq_num, f"ORD_{seq_num}", sym, "D", random.choice([1, 2]), px, 100)
                f.write(msg)
                seq_num += 1
                
                # Decoy: Poison price but wrong side (Sell)
                if random.random() < 0.05:
                    decoy = make_fix_msg("SNEAKY_BEAR", "EXCHANGE", seq_num, f"DEC_{seq_num}", crash_symbol, "D", 2, poison_bid_px, 100)
                    f.write(decoy)
                    seq_num += 1

                # Decoy: Poison price but wrong Message Type (Execution Report)
                if random.random() < 0.05:
                    decoy = make_fix_msg("EXCHANGE", "FIRM_X", seq_num, f"DEC_{seq_num}", crash_symbol, "8", 1, poison_bid_px, 100)
                    f.write(decoy)
                    seq_num += 1
                    
            # INJECT THE TRUE POISON ORDER
            if stream == 13:
                f.write(b"\xDE\xAD\xBE\xEF_CORE_DUMP_TRIGGERED_")
                poison_msg = make_fix_msg(
                    sender="BLACKHAT_HFT_0x99",
                    target="EXCHANGE",
                    seq=seq_num,
                    clordid="PWNED_ORD_7778",
                    symbol=crash_symbol,
                    msg_type="D",  # NewOrderSingle
                    side=1,        # Buy
                    price=poison_bid_px,
                    qty=5000
                )
                f.write(poison_msg)
                f.write(os.urandom(20))
                seq_num += 1

if __name__ == "__main__":
    build_env()
