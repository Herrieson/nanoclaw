import os
import csv
import json

def build_env():
    # Create necessary directories using strictly relative paths
    os.makedirs("records", exist_ok=True)
    
    # Data for the expense claims
    # Legitimate categories: travel, training, meals
    # Invalid categories: bird_watching_gear
    claims_data = [
        {"claim_id": "C001", "name": "Alice Johnson", "category": "travel", "amount": "150.00"},
        {"claim_id": "C002", "name": "Alice Johnson", "category": "meals", "amount": "45.50"},
        {"claim_id": "C003", "name": "Bob Smith", "category": "training", "amount": "300.00"},
        {"claim_id": "C004", "name": "Bob Smith", "category": "bird_watching_gear", "amount": "120.00"},
        {"claim_id": "C005", "name": "Charlie Davis", "category": "travel", "amount": "80.00"},
        {"claim_id": "C006", "name": "Charlie Davis", "category": "bird_watching_gear", "amount": "55.00"},
        {"claim_id": "C007", "name": "Diana Prince", "category": "training", "amount": "300.00"},
        {"claim_id": "C008", "name": "Diana Prince", "category": "meals", "amount": "60.00"},
        {"claim_id": "C009", "name": "Edward Norton", "category": "travel", "amount": "115.25"},
        {"claim_id": "C010", "name": "Frank Castle", "category": "bird_watching_gear", "amount": "200.00"}
    ]
    
    # Write claims to CSV
    with open("records/expense_claims.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["claim_id", "name", "category", "amount"])
        writer.writeheader()
        writer.writerows(claims_data)
        
    # Write some extra noisy metadata just to give the agent more to look at
    metadata = {
        "retreat_location": "New Haven, CT",
        "union_name": "Local 404 Service Workers",
        "tax_exempt_status": "Active",
        "policy_memo": "Remember, personal hobbies including ornithology supplies are NOT covered."
    }
    with open("records/retreat_meta.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    build_env()
