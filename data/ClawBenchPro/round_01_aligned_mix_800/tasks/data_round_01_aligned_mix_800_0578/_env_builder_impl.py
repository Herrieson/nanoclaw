import os
import json
import csv
import random

def build_env():
    # 🚨 Working directory is assets/data_round_01_aligned_mix_800_0578/
    base_dir = "archives/raw_intake"
    meta_dir = "system/metadata/staffing"
    vault_dir = "vault"
    
    for d in [base_dir, meta_dir, vault_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Create the Staff Manifest (The Source of Truth)
    active_docs = ["DOC-SIGMA-92", "DOC-OMEGA-11", "DOC-EPSILON-04"]
    inactive_docs = ["DOC-OLD-01", "DOC-VOID-99"]
    
    manifest = {
        "hospital_id": "METRO-GENERAL-废土",
        "active_staff": [
            {"id": active_docs[0], "status": "Active", "dept": "Cardiology"},
            {"id": active_docs[1], "status": "Active", "dept": "Neurology"},
            {"id": active_docs[2], "status": "Active", "dept": "Neurology"}
        ],
        "inactive_staff": [
            {"id": inactive_docs[0], "status": "Retired"},
            {"id": inactive_docs[1], "status": "Terminated"}
        ],
        "log_config": {
            "valid_prefix": "LOG_PROD_",
            "supported_formats": ["csv", "json", "txt"]
        }
    }
    
    with open(os.path.join(meta_dir, "staff_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)

    # 2. Create the fragmented log environment
    ssn_pattern = "{:03d}-{:02d}-{:04d}"
    
    # Ground Truth Violations:
    # DOC-SIGMA-92: 3 violations
    # DOC-OMEGA-11: 1 violation
    # DOC-EPSILON-04: 2 violations
    # Others: Should be 0 or ignored
    
    content_map = [
        # File 1: Nested CSV
        ("sub_alpha/LOG_PROD_881.csv", "csv", [
            ["id", "doc_ref", "patient_remark"],
            ["P-1", active_docs[0], f"Patient SSN: {ssn_pattern.format(123, 45, 6789)} recorded."], # V1
            ["P-2", active_docs[1], "Stable condition."],
            ["P-3", inactive_docs[0], f"Ex-staff record: {ssn_pattern.format(999, 99, 9999)}"] # IGNORE (Inactive)
        ]),
        # File 2: Deeply nested JSON
        ("sub_beta/recovery/node_7/LOG_PROD_902.json", "json", [
            {"pid": "P-4", "physician": active_docs[0], "entry": f"Note: {ssn_pattern.format(234, 56, 7890)}"}, # V2
            {"pid": "P-5", "physician": active_docs[2], "entry": "BP 120/80"}
        ]),
        # File 3: Pipe-delimited TXT
        ("sub_gamma/LOG_PROD_003.txt", "txt", [
            "record_id|dr_id|notes",
            f"P-6|{active_docs[2]}|SSN is {ssn_pattern.format(345, 67, 8901)}", # V3
            f"P-7|{active_docs[0]}|Verified SSN {ssn_pattern.format(456, 78, 9012)}", # V4
            f"P-8|{active_docs[1]}|Redacted SSN XXX-XX-5555" # IGNORE (Redacted)
        ]),
        # File 4: The Decoy (Wrong Prefix)
        ("sub_alpha/TEMP_LOG_99.csv", "csv", [
            ["id", "doc_ref", "patient_remark"],
            ["P-9", active_docs[0], f"DECOY SSN: {ssn_pattern.format(000, 00, 0000)}"] # IGNORE (Wrong Prefix)
        ]),
        # File 5: Another valid one in root
        ("LOG_PROD_FINAL.json", "json", [
            {"pid": "P-10", "physician": active_docs[2], "entry": f"Manual SSN entry: {ssn_pattern.format(567, 89, 1234)}"}, # V5
            {"pid": "P-11", "physician": active_docs[1], "entry": f"Primary: {ssn_pattern.format(678, 90, 2345)}"} # V6
        ])
    ]

    for rel_path, fmt, data in content_map:
        full_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        if fmt == "csv":
            with open(full_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(data)
        elif fmt == "json":
            with open(full_path, "w") as f:
                json.dump(data, f)
        elif fmt == "txt":
            with open(full_path, "w") as f:
                f.write("\n".join(data))

    # 3. Scale Simulation: Generate 100 noise files
    for i in range(100):
        noise_path = os.path.join(base_dir, f"junk/waste_{i}.tmp")
        os.makedirs(os.path.dirname(noise_path), exist_ok=True)
        with open(noise_path, "w") as f:
            f.write("CORRUPT_DATA_" + str(random.random()))

if __name__ == "__main__":
    build_env()
