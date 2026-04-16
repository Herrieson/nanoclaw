import os
import random

def build_env():
    base_dir = "assets/data_430"
    os.makedirs(base_dir, exist_ok=True)
    
    # We will generate 4 corrupted log files
    # Only "Krakow Parts" orders should be extracted.
    # Total for Krakow Parts should be:
    # File 1: KP-001 (Qty 10, Price 15.50) -> 155.00
    # File 2: KP-002 (Qty 5, Price 40.00) -> 200.00
    # File 3: KP-003 (Qty 100, Price 1.25) -> 125.00
    # File 4: KP-004 (Qty 2, Price 310.00) -> 620.00
    # Grand Total: 155 + 200 + 125 + 620 = 1100.00
    
    file_contents = {
        "raw_orders_1.txt": """SYSTEM ERROR: BUFFER OVERFLOW AT 0x00A1
TXN|SUPPLIER|PART_NUM|QTY|PRICE
1001|Texas Steel|TS-99|50|$10.00
WARN: Missed heartbeat
1002|Krakow Parts|KP-001|10|$15.50
1003|Ohio Plastics|OP-2|200|$0.50
ERR: connection reset by peer""",
        
        "raw_orders_2.txt": """1004|Global Mfg|GM-11|1|$1000.00
1005|Krakow Parts|KP-002|5|$40.00
FATAL: Disk write failure
1006|Texas Steel|TS-100|10|$12.00""",

        "raw_orders_3.txt": """1007|Local Vendor|LV-01|500|$0.10
SYSTEM REBOOT INITIATED...
1008|Krakow Parts|KP-003|100|$1.25
1009|Local Vendor|LV-02|100|$0.20""",

        "raw_orders_4.txt": """1010|Ohio Plastics|OP-3|50|$0.75
1011|Global Mfg|GM-12|2|$500.00
1012|Krakow Parts|KP-004|2|$310.00
END OF LOG"""
    }
    
    for filename, content in file_contents.items():
        filepath = os.path.join(base_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
