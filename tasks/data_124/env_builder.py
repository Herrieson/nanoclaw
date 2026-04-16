import os
import json

def build_env():
    base_dir = "assets/data_124"
    records_dir = os.path.join(base_dir, "records")
    
    os.makedirs(records_dir, exist_ok=True)

    # 1. manual.txt
    manual_content = """
Hey, note to self about the QA thresholds:
For Pulse Oximeters (sometimes I write Pulse Ox or PO), the SpO2 variance cannot be greater than 2.0%. If it's over 2.0, it's a FAIL.
For Infusion Pumps (IP or Pump), the flow rate error margin is strictly 5.0%. Anything above 5.0% error is a FAIL.
Make sure to check all files, I used different formats yesterday.
"""
    with open(os.path.join(base_dir, "manual.txt"), "w") as f:
        f.write(manual_content.strip())

    # 2. records/day1.txt
    day1_content = """
Device: PO-101, Type: Pulse Oximeter, SpO2_var: 1.5% -> Looks good
Device: PO-102, Type: Pulse Ox, SpO2_var: 1.9% -> Cutting it close but fine
Device: PO-103, Type: Pulse Oximeter, SpO2_var: 2.4% -> Trash this one
"""
    with open(os.path.join(records_dir, "day1.txt"), "w") as f:
        f.write(day1_content.strip())

    # 3. records/pump_tests.csv
    csv_content = """device_id,device_type,error_rate
IP-201,Infusion Pump,3.2
IP-202,Infusion Pump,6.5
IP-203,Pump,4.9
"""
    with open(os.path.join(records_dir, "pump_tests.csv"), "w") as f:
        f.write(csv_content.strip())

    # 4. records/messy_notes.log
    log_content = """
[10:00 AM] Tested IP-204, flow error is 1.2%. Very nice.
[10:30 AM] Ugh, PO-104 is giving me a headache. SpO2 variance is 3.1%. Marking as bad.
[11:00 AM] IP-205 is at 5.5% error. Gotta fail it.
[11:30 AM] PO-105 variance 0.8%.
"""
    with open(os.path.join(records_dir, "messy_notes.log"), "w") as f:
        f.write(log_content.strip())

if __name__ == "__main__":
    build_env()
