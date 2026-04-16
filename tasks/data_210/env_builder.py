import os
import shutil

def build_env():
    base_dir = "assets/data_210"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    log_content = """PT-1029 | Drug: Amoxicillin 500mg | Qty: 30 | Dr: D-8812
Patient: PT-9912, Rx: Adderall 20mg xr, quantity: 60, prescriber: 
[PT-5511] -- Oxycodone 10mg -- 15 pills -- Doc: D-1122
pt_id=PT-3321 ; medication=Lisinopril 10mg ; qty=90 ; doctor=D-9988
PT-4444 | Oxycodone 5mg | Qty: 45 | Dr: MISSING
ID: PT-0001 | Med: Ibuprofen 800mg | Amount: 60 | Provider: D-1010
Patient: PT-7777, Rx: adderall 10mg, quantity: 30, prescriber: D-3333
pt_id=PT-8888 ; medication=OXYCODONE 15mg ; qty=20 ; doctor=
[PT-1234] -- Metformin 500mg -- 120 pills -- Doc: MISSING
"""
    
    with open(os.path.join(base_dir, "raw_dispense.log"), "w", encoding="utf-8") as f:
        f.write(log_content)

if __name__ == "__main__":
    build_env()
