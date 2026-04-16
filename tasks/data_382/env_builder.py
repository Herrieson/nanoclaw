import os
import random

def build_env():
    base_dir = "assets/data_382"
    os.makedirs(base_dir, exist_ok=True)

    random.seed(42)
    
    mac_addresses = [
        "00:1A:2B:3C:4D:5E",
        "08:00:27:A1:B2:C3",
        "DC:A6:32:88:99:AA",
        "B8:27:EB:44:55:66"
    ]
    faulty_mac = "00:14:22:01:23:45"
    
    log_entries = []
    
    # Generate 500 lines of normal logs
    for i in range(500):
        mac = random.choice(mac_addresses)
        signal = random.randint(40, 80)
        noise = random.randint(30, 60)
        timestamp = f"10:{random.randint(10, 59):02d}:{random.randint(10, 59):02d}"
        
        log_entries.append(f"[{timestamp}] INFO interface eth0 - MAC {mac} - Signal_Strength: {signal} dBm, Noise_Level: {noise} dBm, Status: OK")
        
        # Random normal events
        if random.random() < 0.1:
            log_entries.append(f"[{timestamp}] DEBUG STP state forwarding for MAC {mac}")

    # Inject faulty MAC logs
    # We want max signal = 95, min noise = 12 for the faulty MAC
    faulty_logs = [
        f"[10:15:01] ERROR interface eth1 - MAC {faulty_mac} - BROADCAST STORM DETECTED",
        f"[10:15:05] WARN interface eth1 - MAC {faulty_mac} - LINK FLAP",
        f"[10:15:10] INFO interface eth1 - MAC {faulty_mac} - Signal_Strength: 95 dBm, Noise_Level: 25 dBm, Status: UNSTABLE",
        f"[10:15:15] INFO interface eth1 - MAC {faulty_mac} - Signal_Strength: 88 dBm, Noise_Level: 12 dBm, Status: UNSTABLE",
        f"[10:15:20] ERROR interface eth1 - MAC {faulty_mac} - BROADCAST STORM DETECTED",
        f"[10:15:25] INFO interface eth1 - MAC {faulty_mac} - Signal_Strength: 90 dBm, Noise_Level: 14 dBm, Status: UNSTABLE"
    ]
    
    # Add a few more random telemetry for faulty mac to blend it
    for i in range(10):
        signal = random.randint(60, 90)
        noise = random.randint(15, 40)
        timestamp = f"10:{random.randint(16, 59):02d}:{random.randint(10, 59):02d}"
        faulty_logs.append(f"[{timestamp}] INFO interface eth1 - MAC {faulty_mac} - Signal_Strength: {signal} dBm, Noise_Level: {noise} dBm, Status: UNSTABLE")
        if random.random() < 0.3:
            faulty_logs.append(f"[{timestamp}] WARN interface eth1 - MAC {faulty_mac} - LINK FLAP")

    all_logs = log_entries + faulty_logs
    
    # Sort logs by timestamp (simple string sort works here due to fixed format)
    all_logs.sort(key=lambda x: x[1:9])
    
    with open(os.path.join(base_dir, "network_logs.txt"), "w") as f:
        f.write("\n".join(all_logs) + "\n")
        
    tech_manual_content = """# Arrakis-9 Firmware Technical Manual
## Section 4.2: Layer-2 Diagnostics and Attenuation Tuning

When dealing with high-density multiplexing, signal attenuation can cause significant packet loss and layer-2 loops.

To calculate the Peak Attenuation Coefficient for a specific hardware address (MAC):
1. Parse the telemetry logs for the target MAC address.
2. Identify the Maximum `Signal_Strength` (in dBm) recorded for this MAC.
3. Identify the Minimum `Noise_Level` (in dBm) recorded for this MAC.
4. Calculate the base differential: (Max_Signal - Min_Noise).
5. Multiply the base differential by the golden ratio constant: `1.618`.
6. Round the final result to exactly 3 decimal places.

*Note: Ensure you only use the telemetry data for the device causing the network anomalies (e.g., link flaps, broadcast storms).*
"""
    with open(os.path.join(base_dir, "tech_manual.md"), "w") as f:
        f.write(tech_manual_content)

if __name__ == "__main__":
    build_env()
