import os
import random
import json

def build_env():
    # 1. Create deeply nested directories
    directories = [
        "docs/schematics",
        "docs/pmic",
        "docs/pmic/registers",
        "docs/sensors",
        "logs/analyzer_dumps/i2c_main",
        "logs/analyzer_dumps/i2c_aux",
        "logs/uart_debug",
        "report"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Fragment 1: Board Revision Strapping (Multi-hop clue 1)
    with open("docs/schematics/hw_strapping_revA.ini", "w") as f:
        f.write("[BOOT_STRAP]\nI2C_ADDR_SEL_PIN = 0\nDEBUG_EN = 1\n")
    
    with open("docs/schematics/hw_strapping_revB.ini", "w") as f:
        f.write("[BOOT_STRAP]\n; Rev B modified the address strap to avoid conflict with the new audio codec\nI2C_ADDR_SEL_PIN = 1\nDEBUG_EN = 1\n")

    # 3. Fragment 2: PMIC Address Map (Multi-hop clue 2)
    address_map = {
        "device": "NXP-832 Power Management IC",
        "bus": "I2C",
        "addressing": {
            "ADDR_SEL_PIN=0": "0x5A",
            "ADDR_SEL_PIN=1": "0x5C"
        }
    }
    with open("docs/pmic/i2c_addr_map.json", "w") as f:
        json.dump(address_map, f, indent=4)

    # 4. Fragment 3: Register Maps with Decoys (Multi-hop clue 3)
    decoy_reg_content = """=== NXP-832 REV 1 (LEGACY) ===
REG_MAP:
[0x01] SYS_STAT (R)
[0x10] VDD_CORE_CTRL (R/W) 
       Absolute Maximum Rating (AMR): 0x50. 
       Warning: Exceeding triggers OVP!
"""
    with open("docs/pmic/registers/rev1_amr.txt", "w") as f:
        f.write(decoy_reg_content)

    real_reg_content = """=== NXP-832 REV 2 (ACTIVE FOR BOARD REV B) ===
DOCUMENT ID: NXP-832-REV2 
REG_MAP:
[0x01] SYS_STAT (R)
[0x10] VDD_CORE_CTRL (R/W) 
       *CRITICAL*: Core voltage trim. 
       Absolute Maximum Rating (AMR) lowered to 0x3F due to thermal issues! 
       WARNING: Exceeding 0x3F triggers hardware OVP -> Hard Lockup (NACK storm).
[0x11] VDD_MEM_CTRL (R/W)
       Max safe rating: 0x50.
"""
    with open("docs/pmic/registers/rev2_amr.txt", "w") as f:
        f.write(real_reg_content)

    # Decoy sensor docs
    with open("docs/sensors/bma400_extract.txt", "w") as f:
        f.write("ADDR: 0x14\nREG[0x00] CHIP_ID\nREG[0x10] ACC_CONFIG\n")

    # 5. Generate Massive Log Fragments (Scale & Noise)
    random.seed(87) # Deterministic
    time_us = 100.000
    
    # We will generate 200 files, each with ~250 lines
    total_shards = 200
    fatal_shard = 142
    fatal_line_idx = 185
    
    for shard_idx in range(total_shards):
        main_log = []
        aux_log = []
        
        main_log.append(f"Saleae Logic Export Part {shard_idx}")
        main_log.append("Timestamp (us) | Bus | Dir | Payload | Status")
        main_log.append("-" * 60)
        
        aux_log.append(f"AUX BUS EXPORT {shard_idx}\n" + "-"*60)
        
        for line_idx in range(250):
            time_us += random.uniform(1.0, 15.0)
            
            # Generate I2C_AUX noise (full of NACKs to confuse)
            if random.random() > 0.5:
                aux_log.append(f"{time_us:011.3f} | I2C_AUX | WR | <START> 0x33 0x01 0xFF <STOP> | NACK")
            
            # Occasionally inject corrupted analyzer frames
            if random.random() < 0.02:
                main_log.append(f"{time_us:011.3f} | [GLITCH] | RX_ERROR | NULL_FRAME | ERROR")
                continue

            # Determine State of Main Bus
            is_post_crash = (shard_idx > fatal_shard) or (shard_idx == fatal_shard and line_idx > fatal_line_idx)
            is_fatal_line = (shard_idx == fatal_shard and line_idx == fatal_line_idx)
            
            if is_post_crash:
                # Post-crash NACK storm
                device = random.choice([0x14, 0x2A, 0x5C])
                main_log.append(f"{time_us:011.3f} | I2C_MAIN | WR  | <START> 0x{device:02X} 0x00 0x00 <STOP> | NACK")
            elif is_fatal_line:
                # THE FATAL WRITE: Device 0x5C, Reg 0x10, Value > 0x3F
                fatal_val = 0x4B
                main_log.append(f"{time_us:011.3f} | I2C_MAIN | WR  | <START> 0x5C 0x10 0x{fatal_val:02X} <STOP> | ACK")
            else:
                # Normal traffic
                device = random.choice([
                    (0x14, 0x00, 0x00), 
                    (0x14, 0x10, random.randint(0x00, 0xFF)), 
                    (0x5C, 0x11, random.randint(0x00, 0x50)), 
                    (0x5C, 0x10, random.randint(0x00, 0x3F)) # Safe writes
                ])
                addr, reg, data = device
                # Add random whitespaces to break naive split() logic
                sp = " " * random.randint(1, 4)
                main_log.append(f"{time_us:011.3f} | I2C_MAIN | WR  | <START>{sp}0x{addr:02X} 0x{reg:02X} 0x{data:02X} <STOP> | ACK")
                
                # Sometime reads
                if random.random() > 0.8:
                    time_us += random.uniform(0.5, 2.0)
                    main_log.append(f"{time_us:011.3f} | I2C_MAIN | RD  | <START> 0x{addr:02X} 0x{reg:02X} <STOP> | ACK")

        # Save Shards
        with open(f"logs/analyzer_dumps/i2c_main/trace_part_{shard_idx:03d}.log", "w") as f:
            f.write("\n".join(main_log))
            
        with open(f"logs/analyzer_dumps/i2c_aux/aux_part_{shard_idx:03d}.log", "w") as f:
            f.write("\n".join(aux_log))

if __name__ == "__main__":
    build_env()
