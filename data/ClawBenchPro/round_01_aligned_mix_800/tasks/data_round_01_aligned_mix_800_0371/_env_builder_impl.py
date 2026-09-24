import os
import json
import base64

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Define the core data
    # Note: We are simulating a "Legacy Binary Format" by base64 encoding a CSV-like string
    tickets_data = [
        "ticket_id,zip_code,assigned_zone,issue",
        "TX-100,78701,North-Transit,Late delivery",
        "TX-101,78702,South-Transit,Driver went to wrong house", # Correct: East
        "TX-102,78703,West-Transit,Package damaged",
        "TX-103,78704,North-Transit,Never arrived",           # Correct: South
        "TX-104,78705,Central-Transit,Left in rain",
        "TX-105,78701,East-Transit,Rude driver",              # Correct: North
        "TX-106,78704,South-Transit,Lost item",
        "TX-107,78702,East-Transit,Tracking broken",
        "TX-108,78705,West-Transit,Delivered to neighbor",     # Correct: Central
        "TX-109,78703,West-Transit,Box crushed"
    ]
    
    binary_content = "\n".join(tickets_data).encode("utf-16") # Specific encoding
    encoded_content = base64.b64encode(binary_content)
    
    # Write the "Legacy" file
    with open("raw_data/dispatch_logs.dat", "wb") as f:
        f.write(encoded_content)

    print("Environment for data_round_01_aligned_mix_800_0371 built successfully.")

if __name__ == "__main__":
    build_env()
