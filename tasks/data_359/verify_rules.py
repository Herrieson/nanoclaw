import os
import json
import csv

def verify():
    state = {
        "report_exists": False,
        "report_headers_correct": False,
        "report_claims_correct": False,
        "payout_file_exists": False,
        "payout_amount_correct": False
    }

    report_path = "avian_claims_report.csv"
    payout_path = "total_payout.txt"

    expected_claims = {"NM-2023-011", "NM-2023-025", "NM-2023-038", "NM-2023-042", "NM-2023-049"}
    expected_payout = 4641.00

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                if [h.strip() for h in headers] == ["ClaimID", "Date", "ZipCode", "Amount", "Species"]:
                    state["report_headers_correct"] = True
                
                found_claims = set()
                for row in reader:
                    if row:
                        found_claims.add(row[0].strip())
                
                if found_claims == expected_claims:
                    state["report_claims_correct"] = True
        except Exception:
            pass

    if os.path.exists(payout_path):
        state["payout_file_exists"] = True
        try:
            with open(payout_path, "r", encoding="utf-8") as f:
                content = f.read().strip().replace('$', '').replace(',', '')
                amount = float(content)
                if abs(amount - expected_payout) < 0.01:
                    state["payout_amount_correct"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
