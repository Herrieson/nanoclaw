import os
import random

def build_env():
    base_dir = "assets/data_19"
    os.makedirs(base_dir, exist_ok=True)
    
    log_file_path = os.path.join(base_dir, "scanner_dump_1024.log")
    
    # We will generate some normal readings, some anomalous readings (> 500 diff), and some garbage.
    addresses = [
        "102 Elm St", "104 Elm St", "108 Elm St", "110 Elm St",
        "205 Maple Dr", "207 Maple Dr", "209 Maple Dr", "211 Maple Dr",
        "300 Oak Ln", "302 Oak Ln", "304 Oak Ln", "308 Oak Ln",
        "415 Pine Ave", "417 Pine Ave", "419 Pine Ave", "421 Pine Ave",
        "550 Cedar Ct", "552 Cedar Ct", "554 Cedar Ct", "556 Cedar Ct"
    ]
    
    anomalous_indices = [2, 7, 11, 18] # 108 Elm St, 211 Maple Dr, 308 Oak Ln, 554 Cedar Ct
    
    with open(log_file_path, "w") as f:
        f.write("START OF DUMP === HANDHELD OS V2.1.4\n")
        f.write("ERR: MEMORY CORRUPTION DETECTED AT SECTOR 4\n")
        
        for i, addr in enumerate(addresses):
            # Insert random garbage lines
            if random.random() < 0.3:
                f.write(f"@@@ binary_garbage 0x{random.randint(1000,9999):X} !##&*()\n")
            
            meter_id = 80000 + i
            prev_reading = random.randint(1000, 9000)
            
            if i in anomalous_indices:
                curr_reading = prev_reading + random.randint(501, 800)
            else:
                curr_reading = prev_reading + random.randint(10, 499)
                
            # Randomly format the log line to make parsing slightly harder
            if random.random() < 0.5:
                f.write(f"TIMESTAMP: 2023-10-24 08:{10+i}:00 | MID: {meter_id} | ADDR: {addr} | PREV: {prev_reading} | CURR: {curr_reading}\n")
            else:
                f.write(f"RECORD -> ADDR: {addr} ; PREV: {prev_reading} ; MID: {meter_id} ; CURR: {curr_reading} ; STAT: OK\n")
                
            # More garbage
            if random.random() < 0.2:
                f.write("WARN: LOW BATTERY\n")

        f.write("EOF\n")

if __name__ == "__main__":
    build_env()
