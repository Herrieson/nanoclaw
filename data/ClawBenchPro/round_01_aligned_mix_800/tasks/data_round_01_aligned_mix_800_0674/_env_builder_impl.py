import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("raw_claims", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Create policy_white_list.csv
    policies = [
        {"Policy_ID": "POL-001", "Limit": 5000},
        {"Policy_ID": "POL-002", "Limit": 12000},
        {"Policy_ID": "POL-003", "Limit": 8500},
        {"Policy_ID": "POL-004", "Limit": 25000},
        {"Policy_ID": "POL-005", "Limit": 3000},
    ]
    
    with open("policy_white_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Policy_ID", "Limit"])
        writer.writeheader()
        writer.writerows(policies)

    # 2. Create raw_claims files (mix of formats and messy data)
    # File 1: CSV with some valid, some invalid IDs
    claims_1 = [
        ["Claim_ID", "Policy_ID", "Claim_Amount"],
        ["C-101", "POL-001", 4500],   # Valid
        ["C-102", "POL-999", 1000],   # Invalid ID
        ["C-103", "POL-002", 15000],  # Over Limit (Limit 12000)
        ["C-104", "POL-003", 8000],   # Valid
    ]
    with open("raw_claims/batch_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(claims_1)

    # File 2: Another CSV with more data
    claims_2 = [
        ["Claim_ID", "Policy_ID", "Claim_Amount"],
        ["C-201", "POL-004", 20000],  # Valid
        ["C-202", "POL-005", 3500],   # Over Limit (Limit 3000)
        ["C-203", "POL-001", 100],    # Valid
        ["C-204", "POL-XYZ", 5000],   # Invalid ID
    ]
    with open("raw_claims/batch_beta.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(claims_2)

    # Summary of valid/non-overlimit claims:
    # C-101 (4500) + C-104 (8000) + C-201 (20000) + C-203 (100) = 32600
    
    # Exceptions:
    # C-102 (Invalid ID), C-103 (Over), C-202 (Over), C-204 (Invalid ID)

if __name__ == "__main__":
    build_env()
