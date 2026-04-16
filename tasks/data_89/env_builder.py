import os
import json

def build_env():
    base_dir = "assets/data_89"
    logs_dir = os.path.join(base_dir, "raw_logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    
    # 1. Compliance Memo
    memo_content = """
INTERNAL MEMO - COMPLIANCE & RISK
DATE: Oct 15, 2023
SUBJECT: Audit for Predatory Lending Indicators

As part of our commitment to community development and fair banking practices, we must identify high-risk loans that may qualify as predatory under our new internal guidelines.

Please flag any transaction that meets BOTH of the following conditions:
1. The Annual Percentage Rate (APR) or Interest Rate is STRICTLY GREATER THAN 35.5%.
2. The loan notes or comments contain ANY of the following target keywords (case-insensitive):
   - "payday"
   - "advance"
   - "title_pledge"

Ensure all flagged records are compiled for immediate review.
"""
    with open(os.path.join(base_dir, "compliance_memo_2023.txt"), "w") as f:
        f.write(memo_content)

    # 2. Old System CSV (Data A)
    csv_content = """id,name,amount,interest_rate,notes
L-101,Maria Garcia,1000,36.0,needed payday loan for rent
L-102,John Doe,500,10.0,payday advance requested
L-103,Alice Smith,2000,40.0,standard personal loan
L-104,Carlos Ruiz,800,35.6,car repair title_pledge
L-105,Eve Adams,1500,35.5,payday issue
"""
    with open(os.path.join(logs_dir, "old_sys_q3.csv"), "w") as f:
        f.write(csv_content)

    # 3. New System JSONL (Data B)
    jsonl_data = [
        {"loan_id": "NL-550", "customer": "Bob Brown", "apr": 12.5, "comments": "clean history"},
        {"loan_id": "NL-551", "customer": "Sarah Connor", "apr": 38.0, "comments": "emergency ADVANCE funds"},
        "CORRUPTED_LINE_IGNORE_ME_NULL_BYTES\x00\x00",
        {"loan_id": "NL-552", "customer": "David Lee", "apr": 39.9, "comments": "no keywords here"},
        {"loan_id": "NL-553", "customer": "Lisa Wong", "apr": 45.0, "comments": "used car TITLE_PLEDGE"},
        {"loan_id": "NL-554", "customer": "Tom Hanks", "apr": 30.0, "comments": "payday loan"}
    ]
    
    with open(os.path.join(logs_dir, "new_sys_q3.log"), "w") as f:
        for item in jsonl_data:
            if isinstance(item, str):
                f.write(item + "\n")
            else:
                f.write(json.dumps(item) + "\n")

    # 4. Another messy CSV with different headers
    csv2_content = """RefNum;Client;Principal;Rate;Description
X-901;Jim Halpert;5000;5.0;mortgage
X-902;Pam Beesly;300;36.1;cash advance for art supplies
X-903;Dwight Schrute;10000;40.0;farm equipment
"""
    with open(os.path.join(logs_dir, "weird_format.csv"), "w") as f:
        f.write(csv2_content)

if __name__ == "__main__":
    build_env()
