import os
import random

def build_env():
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("risk_control", exist_ok=True)

    # 1. Generate Order Book Snapshot Data (Dirty & Non-standard)
    ob_filepath = os.path.join("dumps", "ob_snapshot.dat")
    base_ts = 1716168500120000 # Microseconds timestamp
    
    with open(ob_filepath, "w", encoding="utf-8") as f:
        # Write some messy headers
        f.write("0xDEADBEEF DUMP START\n")
        f.write("FMT_V2: TS||SYM||BIDS[px@vol,px@vol...]||ASKS[px@vol,px@vol...]\n")
        f.write("<<CORE_DUMP_STREAM>>\n")
        
        # Generate normal data
        for i in range(50):
            ts = base_ts + i * 50 + random.randint(-10, 10) # Introduce slight out-of-order
            bids = f"{3000 - i*0.5}@100,{2999 - i*0.5}@200"
            asks = f"{3001 - i*0.5}@50,{3002 - i*0.5}@150"
            line = f"{ts}||XIN9||{bids}||{asks}\n"
            f.write(line)
            
            # Interference symbol
            ts_alt = base_ts + i * 50 + random.randint(1, 5)
            f.write(f"{ts_alt}||YNG2||150.5@10,150.0@20||151.0@5,151.5@10\n")

        # INJECT POISON DATA (Bid > Ask causing negative spread)
        poison_ts = base_ts + 2600
        poison_bid_px = 3050.5  # Abnormally high bid
        poison_ask_px = 3000.0
        # Format: Bid is drastically higher than Ask
        f.write(f"{poison_ts}||XIN9||{poison_bid_px}@500,2995.0@100||{poison_ask_px}@20,3001.0@50\n")
        
        # Generate subsequent data
        for i in range(51, 80):
            ts = base_ts + i * 50
            bids = f"{2975 - (i-50)*0.5}@100"
            asks = f"{2976 - (i-50)*0.5}@50"
            f.write(f"{ts}||XIN9||{bids}||{asks}\n")
            
        f.write("<<EOF>>\n")

    # 2. Generate FIX Engine Logs (Contains SOH \x01 and binary noise)
    SOH = '\x01'
    log_filepath = os.path.join("logs", "fix_engine.log")
    
    def make_fix_msg(sender, target, seq, clordid, symbol, side, price, qty):
        # 8=BeginString, 9=BodyLength, 35=MsgType(D=NewOrderSingle), 49=SenderCompID, 56=TargetCompID
        # 34=MsgSeqNum, 11=ClOrdID, 55=Symbol, 54=Side(1=Buy, 2=Sell), 44=Price, 38=OrderQty, 10=Checksum
        body = f"35=D{SOH}49={sender}{SOH}56={target}{SOH}34={seq}{SOH}11={clordid}{SOH}55={symbol}{SOH}54={side}{SOH}44={price}{SOH}38={qty}{SOH}"
        msg = f"8=FIX.4.2{SOH}9={len(body)}{SOH}{body}10={random.randint(100,255):03d}{SOH}"
        return msg

    with open(log_filepath, "wb") as f:
        # Write some binary garbage simulating TCP fragmentation
        f.write(b"\x12\x34\x56\x78TCP_SEGMENT_FAULT...\n")
        
        # Generate normal FIX logs with ENCRYPTED SenderCompIDs
        seq_num = 1
        for i in range(50):
            px = 3000 - i*0.5
            sender = f"ENC:10{i:03d}A"
            msg = make_fix_msg(sender, "EXCHANGE", seq_num, f"ORD_N_{i}", "XIN9", 1, px, 100)
            f.write(msg.encode('ascii') + b"\n")
            seq_num += 1
            
            # Interference from other symbols
            sender_alt = f"ENC:HED{i}X"
            msg_alt = make_fix_msg(sender_alt, "EXCHANGE", seq_num, f"ORD_A_{i}", "YNG2", 2, 150.5, 50)
            f.write(msg_alt.encode('ascii') + b"\n")
            seq_num += 1
            
        # INJECT POISON FIX MESSAGE (Matches the abnormal bid price 3050.5)
        # 11=ClOrdID, 49=SenderCompID (Encrypted target)
        f.write(b"ERR_BUFF_OVERFLOW:\xde\xad\xbe\xef\n")
        poison_msg = make_fix_msg("ENC:8a9b2c", "EXCHANGE", seq_num, "POISON_HFT_0x9A", "XIN9", 1, poison_bid_px, 500)
        f.write(poison_msg.encode('ascii') + b"\n")
        seq_num += 1
        
        # Write more normal logs
        for i in range(30):
            msg = make_fix_msg("ENC:NORM77", "EXCHANGE", seq_num, f"ORD_L_{i}", "XIN9", 2, 3000.0, 20)
            f.write(msg.encode('ascii') + b"\n")
            seq_num += 1

if __name__ == "__main__":
    build_env()
