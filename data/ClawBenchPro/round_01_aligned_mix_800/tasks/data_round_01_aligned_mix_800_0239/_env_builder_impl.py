import os
import json
import base64

def build_env():
    # Create necessary directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Raw data that will be "encoded" into the bin file
    # Legitimate: Travel, Training, Meals
    # Invalid: Bird Watching Gear (disguised names)
    raw_claims = [
        {"id": "C001", "user": "Alice Johnson", "desc": "Interstate Transport", "amt": 150.00}, # Travel
        {"id": "C002", "user": "Alice Johnson", "desc": "Standard Subsistence", "amt": 45.50},  # Meals
        {"id": "C003", "user": "Bob Smith", "desc": "Skills Workshop", "amt": 300.00},       # Training
        {"id": "C004", "user": "Bob Smith", "desc": "Precision Optics 10x42", "amt": 120.00},# Bird Gear
        {"id": "C005", "user": "Charlie Davis", "desc": "Bus Fare", "amt": 80.00},            # Travel
        {"id": "C006", "user": "Charlie Davis", "desc": "Sibley's Field Reference", "amt": 55.00}, # Bird Gear
        {"id": "C007", "user": "Diana Prince", "desc": "Professional Seminar", "amt": 300.00}, # Training
        {"id": "C008", "user": "Diana Prince", "desc": "Dinner Meeting", "amt": 60.00},      # Meals
        {"id": "C009", "user": "Edward Norton", "desc": "Commuter Rail", "amt": 115.25},      # Travel
        {"id": "C010", "user": "Frank Castle", "desc": "Low-Light Observation Tool", "amt": 200.00} # Bird Gear
    ]
    
    # Encode the data to a "proprietary" .bin format (Base64 of JSON)
    json_str = json.dumps(raw_claims)
    encoded_data = base64.b64encode(json_str.encode('utf-8'))
    
    with open("records/claims_vault.bin", "wb") as f:
        f.write(encoded_data)
        
    # Metadata
    metadata = {
        "retreat_location": "New Haven, CT",
        "system_status": "Legacy Recovery Mode",
        "audit_policy": "Strict adherence to Union Non-Profit Code Section 501(c)."
    }
    with open("records/retreat_meta.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    build_env()
