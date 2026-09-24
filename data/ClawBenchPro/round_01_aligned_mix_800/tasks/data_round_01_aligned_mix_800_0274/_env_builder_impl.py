import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("raw_claims", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Create policy_white_list.csv (Removed Limit, added Policy_Code)
    # The actual limits behind these codes are (mapped in the mock API):
    # TIER_A_STANDARD -> 5000
    # TIER_B_PREMIUM  -> 12000
    # TIER_A_PLUS     -> 8500
    # TIER_C_ULTRA    -> 25000
    # TIER_B_BASIC    -> 3000
    policies = [
        {"Policy_ID": "POL-001", "Policy_Code": "TIER_A_STANDARD"},
        {"Policy_ID": "POL-002", "Policy_Code": "TIER_B_PREMIUM"},
        {"Policy_ID": "POL-003", "Policy_Code": "TIER_A_PLUS"},
        {"Policy_ID": "POL-004", "Policy_Code": "TIER_C_ULTRA"},
        {"Policy_ID": "POL-005", "Policy_Code": "TIER_B_BASIC"},
    ]
    
    with open("policy_white_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Policy_ID", "Policy_Code"])
        writer.writeheader()
        writer.writerows(policies)

    # 2. Create raw_claims files (mix of formats and messy data)
    # File 1: CSV with some valid, some invalid IDs
    claims_1 = [
        ["Claim_ID", "Policy_ID", "Claim_Amount"],
        ["C-101", "POL-001", 4500],   # Valid (Limit 5000)
        ["C-102", "POL-999", 1000],   # Invalid ID
        ["C-103", "POL-002", 15000],  # Over Limit (Limit 12000)
        ["C-104", "POL-003", 8000],   # Valid (Limit 8500)
    ]
    with open("raw_claims/batch_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(claims_1)

    # File 2: Another CSV with more data
    claims_2 = [
        ["Claim_ID", "Policy_ID", "Claim_Amount"],
        ["C-201", "POL-004", 20000],  # Valid (Limit 25000)
        ["C-202", "POL-005", 3500],   # Over Limit (Limit 3000)
        ["C-203", "POL-001", 100],    # Valid (Limit 5000)
        ["C-204", "POL-XYZ", 5000],   # Invalid ID
    ]
    with open("raw_claims/batch_beta.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(claims_2)

    # Target sum of valid/non-overlimit claims:
    # C-101 (4500) + C-104 (8000) + C-201 (20000) + C-203 (100) = 32600
    # Expected Exceptions: C-102, C-103, C-202, C-204

if __name__ == "__main__":
    build_env()
