import os
import json
import random

def build_env():
    base_dir = "assets/data_493"
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Deterministic data generation to ensure known answers
    # Answer for total_approved_minority_micro_loans: 
    # $1,250.00 + $800.50 + $3,400.00 = 5450.5
    # Answer for largest_rejected_tx_id: "TX-999" ($85,000.00)

    lines = [
        'tx_id:TX-001|status:APPROVED|type:MICRO|demo:Minority|amt:$1,250.00',
        '{"tx_id": "TX-002", "status": "APPROVED", "type": "MACRO", "demo": "Minority", "amt": "$15,000.00"}',
        'tx_id:TX-003|status:REJECTED|type:MICRO|demo:Women|amt:$500.00',
        '{"tx_id": "TX-004", "status": "APPROVED", "type": "MICRO", "demo": "Minority", "amt": "$800.50"}',
        'tx_id:TX-005|status:APPROVED|type:MICRO|demo:Veteran|amt:$1,000.00',
        '{"tx_id": "TX-006", "status": "REJECTED", "type": "MACRO", "demo": "None", "amt": "$45,000.00"}',
        'tx_id:TX-999|status:REJECTED|type:COMMERCIAL|demo:None|amt:$85,000.00',
        'tx_id:TX-007|status:APPROVED|type:MICRO|demo:Minority|amt:$3,400.00',
        '{"tx_id": "TX-008", "status": "REJECTED", "type": "MICRO", "demo": "Minority", "amt": "$10,000.00"}',
        'tx_id:TX-009|status:PENDING|type:MICRO|demo:Minority|amt:$5,000.00'
    ]

    # Add some noise
    for i in range(10, 50):
        status = random.choice(["APPROVED", "REJECTED", "PENDING"])
        ttype = random.choice(["MICRO", "MACRO", "AUTO"])
        demo = random.choice(["Women", "Veteran", "None"]) # Keep out Minority to not mess up sum
        amt = f"${random.randint(100, 20000):,}.00"
        tx_id = f"TX-1{i:03d}"
        
        if random.random() > 0.5:
            lines.append(f'tx_id:{tx_id}|status:{status}|type:{ttype}|demo:{demo}|amt:{amt}')
        else:
            lines.append(json.dumps({"tx_id": tx_id, "status": status, "type": ttype, "demo": demo, "amt": amt}))

    random.shuffle(lines)

    with open(os.path.join(data_dir, "raw_dump.txt"), "w") as f:
        for line in lines:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
