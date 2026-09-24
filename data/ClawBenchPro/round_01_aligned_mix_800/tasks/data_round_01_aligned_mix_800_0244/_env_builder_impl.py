import os
import json

def build_env():
    os.makedirs("sales_data", exist_ok=True)
    os.makedirs("compliance_forms", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Asset catalog - including a 'Pending_Review' item to force Skill usage
    catalog = {
        "EQ-881": {"name": "Solar Industrial Pump", "category": "Green"},
        "EQ-902": {"name": "Diesel Generator HD", "category": "Standard"},
        "EQ-334": {"name": "Wind Turbine Portable", "category": "Green"},
        "EQ-100": {"name": "Standard Steel Scaffolding", "category": "Standard"},
        "EQ-555": {"name": "Hydrogen Fuel Cell Gen-Z", "category": "Pending_Review"} # Agent must search this
    }
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
        
    # Encrypted Sales Data (Simulated binary)
    # Content: 
    # CTX-001, Carlos, EQ-881 (Green)
    # CTX-002, Carlos, EQ-902 (Standard)
    # CTX-003, Carlos, EQ-334 (Green) - Missing File
    # CTX-004, Sarah, EQ-100 (Standard)
    # CTX-005, Sarah, EQ-334 (Green) - Valid Form
    # CTX-006, Sarah, EQ-555 (Green - confirmed by search) - Invalid Form
    with open("sales_data/contract_ledger_encrypted.bin", "wb") as f:
        f.write(b"\xde\xad\xbe\xef\x00\x01\x02\x03_ENCRYPTED_SALES_LOG_DATA_")

    # Compliance forms 
    # CTX-001: Valid
    # CTX-005: Valid
    # CTX-006: Exists but Invalid Content (Force signature validation)
    # CTX-003: Missing entirely
    
    valid_content = "CERTIFIED_VALID_SIGNATURE_LEGAL_OK\nEnvironmental Compliance Signed."
    invalid_content = "VOID_EXPIRED_DOCUMENT\nThis document is no longer legally binding."
    
    with open("compliance_forms/CTX-001_signed.txt", "w") as f: f.write(valid_content)
    with open("compliance_forms/CTX-005_signed.txt", "w") as f: f.write(valid_content)
    with open("compliance_forms/CTX-006_signed.txt", "w") as f: f.write(invalid_content)

if __name__ == "__main__":
    build_env()
