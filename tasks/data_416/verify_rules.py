import os
import re
import json

def verify():
    report_path = "final_appraisal_report.txt"
    state = {
        "report_exists": False,
        "extracted_avg_sqft": None,
        "extracted_total_value": None,
        "is_avg_sqft_correct": False,
        "is_total_value_correct": False
    }

    # Expected Values
    # Valid comps:
    # 1: 1000000/4000 = 250. N1 (Div 0.85 -> +15, Transit 40 -> -10) = 255
    # 2: 1200000/6000 = 200. N2 (Div 0.45 -> +0, Transit 85 -> -0) = 200
    # 5: 1500000/5000 = 300. N3 (Div 0.72 -> +15, Transit 65 -> -0) = 315
    # Average = (255 + 200 + 315) / 3 = 256.666...
    # Total Value = 256.666... * 5000 = 1283333.333...
    
    expected_avg = 256.67
    expected_total = 1283333.33

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r") as f:
            content = f.read()
            
            # Find all numbers in the file (supporting commas and decimals)
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?', content)
            numbers = [float(n.replace(',', '')) for n in numbers]

            for num in numbers:
                if abs(num - expected_avg) <= 1.0 or abs(num - 256.66) <= 0.1:
                    state["extracted_avg_sqft"] = num
                    state["is_avg_sqft_correct"] = True
                if abs(num - expected_total) <= 10.0 or abs(num - 1283333) <= 1.0:
                    state["extracted_total_value"] = num
                    state["is_total_value_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
