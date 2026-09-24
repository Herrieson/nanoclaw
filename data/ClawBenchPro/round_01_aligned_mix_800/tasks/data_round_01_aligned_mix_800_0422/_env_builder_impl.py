import os
import json
import random
import datetime

def build_env():
    # Create the messy directory structure
    base_dirs = [
        "dump_site/archives/legacy_certs",
        "dump_site/registry/current",
        "dump_site/raw_transmissions/corrupted",
        "dump_site/raw_transmissions/active"
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Fragmented & Conflicting Certifications
    # Legacy data (should be ignored if newer exists or filtered by Agent)
    legacy_certs = {
        "FiberOptic": ["Old Man Jenkins", "Sarah Connor"],
        "Cat6": ["Sarah Connor", "John Doe"]
    }
    with open("dump_site/archives/legacy_certs/certs_v1_deprecated.json", "w") as f:
        json.dump(legacy_certs, f)

    # Current certs split into fragments
    cert_frag_1 = {"FiberOptic": ["Maria Garcia", "David Kim", "John Doe"]}
    cert_frag_2 = {"Cat6": ["Maria Garcia", "Tom Smith", "Sarah Lee", "John Doe"]}
    
    with open("dump_site/registry/current/auth_fragment_alpha.json", "w") as f:
        json.dump(cert_frag_1, f)
    
    # Hidden cert in a text log
    with open("dump_site/registry/current/sys_log_update.txt", "w") as f:
        f.write("TIMESTAMP: 2023-10-25\nACTION: UPDATE_REGISTRY\nADD_CERT: [Sarah Lee] -> [FiberOptic]\nNOTE: Verified field test.")

    # 2. Scale Simulation: Massive Transmission Logs
    names_pool = ["Maria Garcia", "David Kim", "John Doe", "Tom Smith", "Sarah Lee", "Alex P", "Zack W", "Linda B"]
    # Qualified: Maria, David, John, Tom, Sarah
    
    for i in range(500):
        # Generate 500 files, mostly noise
        filename = f"dump_site/raw_transmissions/active/log_{i:04d}.txt"
        is_noise = random.random() < 0.7
        
        with open(filename, "w") as f:
            if is_noise:
                f.write(f"NOISE_PACKET_{random.randint(1000, 9999)}\nSTATUS: {random.choice(['DROPPED', 'TIMEOUT'])}\n")
            else:
                name = random.choice(names_pool)
                # Mix of valid and invalid hours
                hours = random.choice(["5", "8", "-10", "NaN", "3", "unknown", "12", "0"])
                f.write(f"SOURCE: Volunteer_Portal\nUSER: {name}\nHOURS_PROVIDED: {hours}\nSHIFT: Saturday_Core\n")

    # Add some deceptive data in the 'corrupted' folder
    for i in range(50):
        with open(f"dump_site/raw_transmissions/corrupted/dead_log_{i}.bak", "w") as f:
            f.write("ERROR: DATA_CORRUPTION_DETECTED\nUSER: Maria Garcia\nHOURS_PROVIDED: 999")

    # Ensure at least some guaranteed valid data for the qualified
    guaranteed = [
        ("Maria Garcia", "10"),
        ("David Kim", "5"),
        ("John Doe", "4"),
        ("Tom Smith", "6"),
        ("Sarah Lee", "7")
    ]
    for i, (name, hr) in enumerate(guaranteed):
        with open(f"dump_site/raw_transmissions/active/fixed_signal_{i}.txt", "w") as f:
            f.write(f"USER: {name}\nHOURS_PROVIDED: {hr}\n")

if __name__ == "__main__":
    build_env()
