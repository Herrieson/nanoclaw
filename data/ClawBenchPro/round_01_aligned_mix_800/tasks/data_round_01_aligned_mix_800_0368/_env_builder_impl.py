import os
import json
import base64
import struct

def build_env():
    # Create required directories
    os.makedirs("raw_feedback", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0368", exist_ok=True)
    
    # Dataset 1: Obfuscated proprietary binary format with customer_ids
    log1_data = [
        {"customer_id": "ID_881", "comment": "The store needs more diversity in its product lines.", "date": "2023-10-01"},
        {"customer_id": "ID_882", "comment": "Prices are getting way too high.", "date": "2023-10-02"},
        {"customer_id": "ID_883", "comment": "The wheelchair ramp is blocked by the new display. Terrible Accessibility.", "date": "2023-10-02"},
        {"customer_id": "ID_884", "comment": "Great lighting in the store.", "date": "2023-10-03"}
    ]
    
    with open("raw_feedback/export_A.bdat", "wb") as f:
        json_bytes = json.dumps(log1_data).encode('utf-8')
        # Proprietary header: 'POS_BDAT', followed by length, followed by XOR obfuscated data
        f.write(b'POS_BDAT')
        f.write(struct.pack('>I', len(json_bytes)))
        obfuscated = bytes([b ^ 0x42 for b in json_bytes])
        f.write(obfuscated)
        
    # Dataset 2: Base64 JSON Lines with customer_ids
    hidden_data = [
        {"customer_id": "ID_885", "comment": "I loved the cultural diversity event last week!", "date": "2023-10-04"},
        {"customer_id": "ID_886", "comment": "Staff was rude to me.", "date": "2023-10-04"},
        {"customer_id": "ID_887", "comment": "Accessibility to the restrooms is severely lacking.", "date": "2023-10-05"}
    ]
    
    with open("raw_feedback/system_dump.txt", "w", encoding="utf-8") as f:
        f.write("POS_SYSTEM_EXPORT_V1.2\n")
        f.write("FORMAT: BASE64 ENCODED JSON LINES\n")
        for record in hidden_data:
            json_str = json.dumps(record)
            b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            f.write(b64_str + "\n")

if __name__ == "__main__":
    build_env()
